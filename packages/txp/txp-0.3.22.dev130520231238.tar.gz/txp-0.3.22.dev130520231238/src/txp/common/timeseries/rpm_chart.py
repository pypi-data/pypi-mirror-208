import plotly.graph_objects as go
import dataclasses
from txp.common.timeseries.time_series_interval import TimeSeriesInterval
import pandas as pd
import numpy as np


@dataclasses.dataclass
class RpmChart:
    interval: TimeSeriesInterval
    dataframe: pd.DataFrame

    def _get_x_y_values(self) -> np.array:
        # Select the desired columns and create a copy of the DataFrame
        df_transformed = self.dataframe.loc[
            :, ["observation_timestamp", "rpm"]
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

        df_transformed["rpm"] = df_transformed["rpm"].apply(lambda x: round(x[0], 2))

        return df_transformed["observation_timestamp"], df_transformed["rpm"]

    def get_plot(self) -> go.Figure:
        # Define x and y values
        x_values, y_values = self._get_x_y_values()

        # Create the figure
        fig = go.Figure(
            data=go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines+markers",
            )
        )

        # Customize the layout
        fig.update_layout(
            title="Velocidad del motor RPM",
            xaxis_title="Tiempo",
            yaxis_title="RPM",
            font=dict(size=16),
            width=800,
            height=600,
            yaxis=dict(
                range=[0, 2000]  # Set the range of y-axis
            )
        )

        return fig

