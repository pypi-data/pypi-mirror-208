"""
    This file contains the Vibration Analysis
    code that supports all the Graphs generation
    for expert analysis.
"""
from typing import List, Dict
import plotly.graph_objects as go
import pytz
import pandas as pd
import numpy as np
from txp.common.timeseries.time_series_interval import VibrationIntervalOption, TimeSeriesInterval
from txp.common.utils.plotter_utils import FFTPlotter
import dataclasses
import logging
from txp.common.config import settings
log = logging.getLogger(__name__)
log.setLevel(settings.txp.general_log_level)


# Accessible Constants values
# Provide some constant values that can be used across the client code
# To determine which type of plotly object is being processed
SIGNAL_TRACE_TYPE_KEY='signal-type'
SIGNAL_TRACE_TYPE_VALUE='signal-trace'  # Describes the trace as a Signal Trace in the plot
FAILURE_FREQUENCY_TRACE_VALUE='failure-frequency-trace'  # Describes the trace as a Failure Frequency trace
_SIGNAL_FIELD = "signal"

@dataclasses.dataclass
class VibrationCascadeGraph:
    """This object represents the Cascade graph of a list of 3D vibration curves

    Args:
        sample_distribution: The sample distribution used to build this graph.
        raw_signals: The list of raw signals pulled from the tabular database.
        machine_id: The ID of the machine to which the signals belong to.
        num_axis: The num of axis measured by the sensor.
    """
    sample_distribution: VibrationIntervalOption
    sample_interval: TimeSeriesInterval
    dataset: pd.DataFrame
    machine_id: str
    tenant_id: str
    num_axis: int = 3
    sampling_frequency: int = 3611 # The sampling frequency varies for the sensor hardware

    def __post_init__(self):
        self._x_axis_name = "Time"
        self._y_axis_name = "Frequency (Hz)"
        self._z_axis_name = "Amplitude (A)"
        self._mean_trace_name = "Arithmetic mean"
        self.dataset["rpm"] = self.dataset["rpm"].apply(lambda x: round(x[0], 2))

    def _get_rpm_bins(self) -> List[float]:
        """Returns a List of float values to specify the bins of a cut
        operation on the `rpm` column values"""
        bins = []
        for i in range(0, 2200, 20):
            bins.append(float(i))

        return bins

    def _get_signals_by_greatest_rpm(self) -> pd.DataFrame:
        """Returns the processed signals given the VibrationIntervalOption

        Based on the value `self.sample_distribution`, the code will process
        the downloaded `self.dataset` to produced a summarized view of the data.
        """
        # Add the rpm_cat column in order to categorize by RPM value
        self.dataset['rpm_cat'] = pd.cut(self.dataset['rpm'], bins=self._get_rpm_bins())

        # Group the DF by the `rpm_cat` groups
        df_by_rpm = self.dataset.groupby(['rpm_cat'])

        # Get the rpm_cat with most elements in it
        major_group = df_by_rpm.count().apply(lambda x: x.sort_values(ascending=False))
        filtered_dataset = df_by_rpm.get_group(major_group.index[0])

        return filtered_dataset

    def _filter_by_std(self, df: pd.DataFrame, multiplier: float = 2.5) -> pd.DataFrame:
        """Filter the dataset by the standard deviation of `rpm` column and
        with a multiplier factor of +- 2.5 as default"""
        # filter the DataFrame using boolean indexing to keep only rows with RPM within 2.5 standard deviations
        rpm_std = df['rpm'].std()
        filtered_df = df[
            (df['rpm'] >= df['rpm'].mean() - multiplier * rpm_std) & (df['rpm'] <= df['rpm'].mean() + multiplier * rpm_std)
        ]
        return filtered_df

    @staticmethod
    def change_utc_timezone(timestamp):
        import pytz
        utc = pytz.timezone("UTC")
        timezone = pytz.timezone("America/Mexico_City")
        date_time = pd.to_datetime(timestamp)
        localized_timestamp = utc.localize(date_time)
        new_timezone = localized_timestamp.astimezone(timezone)
        return new_timezone

    def _get_plotly_traces(self, df: pd.DataFrame):
        if self.sample_distribution is  VibrationIntervalOption.FULL_DETAILED:
            return self.get_full_detailed_traces(df)
        elif self.sample_distribution is VibrationIntervalOption.HOURLY_AVG:
            return self.get_hourly_avg_traces(df)

    def get_hourly_avg_traces(self, df: pd.DataFrame):
        # Convert the observation timestamp column to a datetime object
        df['observation_timestamp'] = pd.to_datetime(df['observation_timestamp'])
        # Round the timestamp down to the nearest hour
        df['hour'] = df['observation_timestamp'].dt.floor('H')
        grouped_by_hour = df.groupby('hour')
        samples_scatters = []
        for group_name, group_df in grouped_by_hour:
            hour_traces_mean = np.mean(
                np.array(group_df["signal"].apply(lambda x: list(map(lambda xx: xx['values'], x))).tolist()),
                axis=0,
                dtype=np.float64
            )

            signal_ts = group_name
            rpm = group_df['rpm'].mean()
            traces_3d = []
            for i, signal_mean in enumerate(hour_traces_mean):
                plt = FFTPlotter(
                    signal_mean,
                    None,
                    3611
                )
                trace = go.Scatter3d(
                    x=[self.change_utc_timezone(signal_ts).strftime(
                        "%Y-%M-%D \n %H:%M:%S"
                    )] * plt.frequency_axis.__len__(),
                    y=plt.frequency_axis,
                    z=plt.sample_count * np.abs(plt.signal_frequency_amplitude_axis),
                    mode="lines",
                    visible=True,
                    name=f"{rpm:.2f} RPM",
                    customdata=(SIGNAL_TRACE_TYPE_VALUE,)
                )
                traces_3d.append(trace)

            samples_scatters.append(traces_3d)

        return samples_scatters

    def get_full_detailed_traces(self, df):
        # Multidimensional array containing all the traces for an specific axis
        samples_scatters = []

        # Number of axis
        dimensions = df.iloc[1][_SIGNAL_FIELD].size
        for i, row in df.iterrows():
            signal_ts = None
            rpm = None
            axis_plots_signal = []
            for axis in range(0, dimensions):
                plt = FFTPlotter(
                    row[_SIGNAL_FIELD][axis]["values"],
                    None,
                    3611
                )
                if not signal_ts:
                    signal_ts = row["observation_timestamp"]
                    rpm = row["rpm"]
                axis_plots_signal.append(plt)

            traces_3d = []
            for idx, axis_plt in enumerate(axis_plots_signal):
                trace = go.Scatter3d(
                    x=[self.change_utc_timezone(signal_ts).strftime(
                        "%Y-%M-%D \n %H:%M:%S"
                    )] * axis_plt.frequency_axis.__len__(),
                    y=axis_plt.frequency_axis,
                    z=axis_plt.sample_count * np.abs(axis_plt.signal_frequency_amplitude_axis),
                    mode="lines",
                    visible=True,
                    name=f"{rpm:.2f} RPM",
                    customdata=(SIGNAL_TRACE_TYPE_VALUE,)
                )
                traces_3d.append(trace)

            samples_scatters.append(traces_3d)

        return samples_scatters

    def get_fig(self) -> List[go.Figure]:
        biggest_rpm_ds = self._get_signals_by_greatest_rpm()
        biggest_rpm_ds = self._filter_by_std(biggest_rpm_ds)
        scattered_traces = self._get_plotly_traces(biggest_rpm_ds)
        figs = []

        for i in range(3):
            traces = []
            for fft_trace in scattered_traces:
                traces.append(fft_trace[i])

            traces.reverse()
            fig = go.Figure(
                data=traces,
                layout=go.Layout(
                    scene=dict(
                        xaxis=dict(title="tiempo"),
                        yaxis=dict(title="Hz"),
                        zaxis=dict(title="A"),
                    )
                )
            )

            camera = dict(eye=dict(x=5, y=5, z=0.1))
            fig.update_layout(
                autosize=True,
                # margin=dict(l=240, r=240, t=120, b=120),
                scene=dict(aspectmode="manual", aspectratio=dict(x=15, y=10, z=3)),
                scene_camera=camera,
                height=720,
            )

            figs.append(fig)

        return figs

    @staticmethod
    def valid_interval_option(
        analisis_kind: VibrationIntervalOption,
        timeseries_interval: TimeSeriesInterval
    ) -> bool:
        if analisis_kind is VibrationIntervalOption.FULL_DETAILED:
            return timeseries_interval.diff() < (3600 * 5)  #  5 hours for detailed

        if analisis_kind is VibrationIntervalOption.HOURLY_AVG:
            return timeseries_interval.diff() < 172800  # 5 days for hourly analysis

        return True
