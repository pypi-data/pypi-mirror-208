import plotly.graph_objects as go
import dataclasses
from txp.common.timeseries.time_series_interval import TimeSeriesInterval
import pandas as pd
import numpy as np


@dataclasses.dataclass
class TemperatureChart:
    interval: TimeSeriesInterval
    dataframe: pd.DataFrame

    def _get_x_y_values(self) -> np.array:
        # Select the desired columns and create a copy of the DataFrame
        df_transformed = self.dataframe.loc[
            :, ["observation_timestamp", "temperature"]
        ].copy()

        # Apply the datetime conversion and timezone localization/conversion to the 'timestamp' column
        df_transformed["observation_timestamp"] = pd.to_datetime(
            df_transformed["observation_timestamp"]
        )
        df_transformed["observation_timestamp"] = (
            df_transformed["observation_timestamp"]
            .dt.tz_localize("UTC")
            .dt.tz_convert("America/Denver")
        )

        return df_transformed["observation_timestamp"], df_transformed["temperature"]

    def get_plot(self) -> go.Figure:
        # Define x and y values
        x_values, y_values = self._get_x_y_values()

        # Define z values
        # Replace with your actual temperature data
        z_values = np.random.rand(100, 100) * 10

        # Create the figure
        fig = go.Figure(
            data=go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines+markers"
            )
        )

        # Customize the layout
        fig.update_layout(
            title="Temperature 2D Curve",
            xaxis_title="Tiempo",
            yaxis_title="Temperatura",
            font=dict(size=16),
            width=800,
            height=600,
        )

        return fig
