"""
This file contains the definition of data objects used across the application.
"""
import dataclasses
import enum
from typing import List, Dict
import plotly.graph_objects as go
import pytz
import pandas as pd
import numpy as np
from txp.common.utils.plotter_utils import FFTPlotter


# Accessible Constants values
# Provide some constant values that can be used across the APP code
# To determine which type of plotly object is being processed
SIGNAL_TRACE_TYPE_KEY='signal-type'
SIGNAL_TRACE_TYPE_VALUE='signal-trace'  # Describes the trace as a Signal Trace in the plot
FAILURE_FREQUENCY_TRACE_VALUE='failure-frequency-trace'  # Describes the trace as a Failure Frequency trace


def add_vertical_3d_failure_freq(figure, freq_y):
    """Adds a vertical surface in the XYZ plane, in order to show a
    visual guide for the failure frequencies.

    Args
        figure: a json plotly figure to add the freq_y vertical surface.
        freq_y: the value of Y in the plotly figure. This is the frequency
            axis.
    """
    x_values = []
    max_z_val = 0

    # Gets all the X-values (datetime axis) active in the plot.
    # Gets the max_z_val found
    for scatter_data in figure["data"]:
        if scatter_data['customdata'][0] == SIGNAL_TRACE_TYPE_VALUE:
            x_values.append(scatter_data["x"][0])
            max_z_val = max(max_z_val, np.max(scatter_data["z"]))

    # Create the vertical plane
    zz = np.linspace(0, max_z_val, 100)
    XX, ZZ = np.meshgrid(x_values, zz)
    YY = freq_y * np.ones(XX.shape)

    # Adds the surface to the plot. The `customdata` attribute value
    #   allows to identify this trace as a non-signal trace.
    fault_surface = go.Surface(
        x=XX,
        y=YY,
        z=ZZ,
        showscale=False,
        opacity=0.2,
        customdata=(FAILURE_FREQUENCY_TRACE_VALUE,)
    )
    figure["data"].append(fault_surface.to_plotly_json())

    return figure


@dataclasses.dataclass
class FrequencyAmplitudeVariationGraph:
    """Represents the 2D Graph to view the variation of amplitude for the
    given instance."""

    x_values: List  # should be the dates
    y_values: List  # should be the Amplitude values
    freq: float  # the frequency value selected by the user

    def get_fig(self) -> go.Figure:
        line = go.Scatter(x=self.x_values, y=self.y_values, showlegend=False)
        fig = go.Figure()
        fig.add_trace(line)
        fig.update_layout(
            title=f"Frequency Variation over time for {self.freq:.2f} Hz.",
            xaxis_title="Tiempo",
            yaxis_title="Amplitude",
        )
        return fig


@dataclasses.dataclass
class AreaVariationGraph:
    """Represents the 2D line of the variation of the area for a given
    list of lines"""

    x_values: List  # should be the dates
    y_values: List  # should be the Amplitude values

    def get_fig(self) -> go.Figure:
        line = go.Scatter(x=self.x_values, y=self.y_values, showlegend=False)
        fig = go.Figure()
        fig.add_trace(line)
        fig.update_layout(
            title=f"Area variation over time for selected samples",
            xaxis_title="Tiempo",
            yaxis_title="Area under the line",
        )
        return fig
