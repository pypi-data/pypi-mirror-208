import dash_bootstrap_components as dbc
import pytz
from dash import Input, Output, dcc, html, callback, State
import plotly.graph_objects as go
from typing import List, Dict
import dash
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, DiskcacheManager, ctx, Dash
from txp.common import timeseries
from txp.common.timeseries.time_series_interval import (
    VibrationIntervalOption,
    TimeSeriesInterval,
)
from txp.common.timeseries.vibration_analysis import VibrationCascadeGraph
from txp.dashboard.pages.styles import *
import os
import dash_mantine_components as dmc

# TODO: This might be a problem. The logging configuration is being taken from `txp` package
from txp.common.config import settings
from numpy import trapz
import logging
import time
from datetime import datetime, date, timedelta
import txp.dashboard.data_objects as entities
import google.cloud.firestore as firestore
from google.oauth2 import service_account
from google.cloud import bigquery
import txp.dashboard.auth as auth

log = logging.getLogger(__name__)
log.setLevel(settings.txp.general_log_level)

#####################################################
# Backend cache for long running callbacks. We configure the local recommended.
# More info here: https://dash.plotly.com/background-callbacks
#####################################################
import diskcache

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

#####################################################
# Register Page on the dash pages
#####################################################
dash.register_page(__name__)


####################################################
# DECLARE LINK COMPONENT TO INSPECT LINK ADDRESS
# SEARCHING AUTH RESPONSE
###################################################
LOCATION_URL = dcc.Location(id='vibration-analysis-url', refresh=True)


#####################################################
# Dash Components Declaration
# From here on, you'll see the declaration of components
# that are in the Vibration Analysis View.
# Components that requires input values to render, will be setup
# with the helper function "init_view_components"
#####################################################
X_AXIS_GRAPH_ID = "x-axis-graph"
X_AXIS_AMP_VAR_FOR_FREQ_GRAPH_ID = "x-axis-amp-var-for-freq-graph"
X_AXIS_FFT_AREA_VAR_PLOT_ID = "x-axis-fft-area-var-graph"
X_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON_ID = "x-axis-fft-area-var-graph-radio-option"
Y_AXIS_GRAPH_ID = "y-axis-graph"
Y_AXIS_AMP_VAR_FOR_FREQ_GRAPH_ID = "y-axis-amp-var-for-freq-graph"
Y_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON_ID = "y-axis-fft-area-var-graph-radio-option"
Y_AXIS_FFT_AREA_VAR_PLOT_ID = "y-axis-fft-area-var-graph"
Z_AXIS_GRAPH_ID = "z-axis-graph"
Z_AXIS_AMP_VAR_FOR_FREQ_GRAPH_ID = "z-axis-amp-var-for-freq-graph"
Z_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON_ID = "z-axis-fft-area-var-graph-radio-option"
Z_AXIS_FFT_AREA_VAR_PLOT_ID = "z-axis-fft-area-var-graph"
X_AXIS_GRAPH_TAB_ID = "x-axis-graph-tab"
Y_AXIS_GRAPH_TAB_ID = "y-axis-graph-tab"
Z_AXIS_GRAPH_TAB_ID = "z-axis-graph-tab"
TRIDIMENSIONAL_GRAPHS_TABS_ID = "3d-graphs-tabs"
TENANT_ID_INPUT_ID = "tenant-id-input"
MACHINE_ID_INPUT_ID = "machine-id-input"
VISUALIZATION_PERIOD_INPUT_ID = "visualization-period-input"
SENSOR_TYPE_INPUT_KEY = "vibration-sensor-input"
SHOW_DATA_BUTTON_ID = "show-data-btn"
SHOW_DATA_BUTTON_SPINNER_ID = "show-data-3d-spinner"
VIEW_TITLE_DIV_ID = "vibration-analysis-div"
LOADING_CONTENT_WRAPPER_ID = "vibration-analysis-view-content-wrapper"
ALL_AXIS_CASCADE_GRAPHS_IDS = [X_AXIS_GRAPH_ID, Y_AXIS_GRAPH_ID, Z_AXIS_GRAPH_ID]
ALL_AXIS_AMP_VAR_FOR_FREQ_IDS = [
    X_AXIS_AMP_VAR_FOR_FREQ_GRAPH_ID,
    Y_AXIS_AMP_VAR_FOR_FREQ_GRAPH_ID,
    Z_AXIS_AMP_VAR_FOR_FREQ_GRAPH_ID,
]
ALL_AXIS_AREA_VAR_IDS = [
    X_AXIS_FFT_AREA_VAR_PLOT_ID,
    Y_AXIS_FFT_AREA_VAR_PLOT_ID,
    Z_AXIS_FFT_AREA_VAR_PLOT_ID,
]
ALL_AXIS_AMP_VAR_FOR_FREQ_RADIO_BUTTONS = [
    X_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON_ID,
    Y_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON_ID,
    Z_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON_ID
]

div_view_title = html.Div(
    html.H2("Análisis de Vibraciones"),
    id=VIEW_TITLE_DIV_ID,
)

div_tenant_id = html.Div(
    [html.P("Cliente"), dcc.Dropdown([""], id=TENANT_ID_INPUT_ID, value="")]
)

div_machine_id = html.Div(
    [html.P("Equipo"), dcc.Dropdown([], id=MACHINE_ID_INPUT_ID, value="")]
)

div_visualization_period = html.Div(
    [html.P("Período"), dcc.Dropdown([], id=VISUALIZATION_PERIOD_INPUT_ID, value="")]
)

div_vibration_sensor = html.Div(
    [html.P("Sensor"), dcc.Dropdown([], id=SENSOR_TYPE_INPUT_KEY, value="")]
)

#######################################################
# Components declaration to select analysis time lapses
#######################################################
VIBRATION_INTERVAL_VISUALIZATION_DROPDOWN_ID = "vibration-visualization-interval-input"
analysis_type_values = list(map(lambda n: n.readable, list(VibrationIntervalOption)))


VIBRATION_INTERVAL_VISUALIZATION_DROPDOWN_DIV = html.Div(
    [
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Tipo de Análisis"),
                        dcc.Dropdown(
                            analysis_type_values,
                            id=VIBRATION_INTERVAL_VISUALIZATION_DROPDOWN_ID,
                            value=analysis_type_values[0],
                        ),
                    ],
                    width=3
                )
            ]
        ),
    ]
)

VIBRATION_INTERVAL_START_DATE_INPUT_ID = "vibration-interval-start-date-input"
VIBRATION_INTERVAL_END_DATE_INPUT_ID = "vibration-interval-end-date-input"
VIBRATION_INTERVAL_START_TIME_ID = "vibration-interval-start-time-in"
VIBRATION_INTERVAL_END_TIME_ID = "vibration-interval-end-time-in"
VIBRATION_INTERVAL_INPUT = dbc.Row(
    [
        dbc.Col(
            dmc.DatePicker(
                id=VIBRATION_INTERVAL_START_DATE_INPUT_ID,
                label="Rango de fecha",
                minDate=date(2020, 8, 5),
                value=datetime.now().date(),
                inputFormat="DD-MM-YYYY",
            )
        ),
        dbc.Col(
            dmc.DatePicker(
                id=VIBRATION_INTERVAL_END_DATE_INPUT_ID,
                label="Rango de fecha",
                minDate=date(2020, 8, 5),
                value=datetime.now().date(),
                inputFormat="DD-MM-YYYY",
            )
        ),
        dbc.Col(
            dmc.TimeInput(
                label="Hora Inicio",
                format="24",
                disabled=True,
                id=VIBRATION_INTERVAL_START_TIME_ID,
                value=datetime.now().replace(microsecond=0),
            )
        ),
        dbc.Col(
            dmc.TimeInput(
                label="Hora Fin",
                format="24",
                disabled=True,
                id=VIBRATION_INTERVAL_END_TIME_ID,
                value=datetime.now().replace(microsecond=0),
            )
        )
    ]
)

btn_show_data = html.Div(
    [
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        id=SHOW_DATA_BUTTON_ID,
                        children=["Ver Datos"],
                        n_clicks=0,
                        color="primary",
                        className="me-1",
                    ),
                    width=2,
                )
            ],
            justify="start",
        ),
    ]
)

WRONG_INTERVAL_ALERT_ID = "wrong-interval-alert"
NO_DATA_FOUND_ALERT_ID = "no-data-found-alert"
INVALID_INTERVAL_ALERT = dmc.Alert(
    "El intervalo de tiempo no es compatible con el tipo de análisis. "
    "Intente seleccionar otro intervalo mas corto.",
    id=WRONG_INTERVAL_ALERT_ID,
    color="red",
    withCloseButton=True,
    hide=True,
)
NO_DATA_FOUND_ALERT = dmc.Alert(
    "No se encuentra data para el intervalo introducido. ",
    id=NO_DATA_FOUND_ALERT_ID,
    color="red",
    withCloseButton=True,
    hide=True
)

data_selection_card_row = dbc.Spinner(
    dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(div_tenant_id),
                        dbc.Col(div_machine_id),
                        dbc.Col(div_visualization_period),
                        dbc.Col(div_vibration_sensor),
                    ]
                ),
                dbc.Row([dbc.Col(VIBRATION_INTERVAL_VISUALIZATION_DROPDOWN_DIV)]),
                dbc.Row([dbc.Col(VIBRATION_INTERVAL_INPUT)]),
                dbc.Row([
                    INVALID_INTERVAL_ALERT,
                ]),
                dbc.Row([
                    NO_DATA_FOUND_ALERT
                ]),
                dbc.Row(btn_show_data),
            ]
        )
    ),
    type="grow",
    color="primary",
    spinner_style={"position": "absolute", "left": "50%", "top": "50px"},
)

X_AXIS_GRAPH_3D_GRAPH = dcc.Graph(
    id=X_AXIS_GRAPH_ID,
)

X_AXIS_AMP_VAR_FOR_FREQ_GRAPH = dcc.Graph(id=X_AXIS_AMP_VAR_FOR_FREQ_GRAPH_ID)

X_AXIS_AREA_VAR_GRAPH = dcc.Graph(id=X_AXIS_FFT_AREA_VAR_PLOT_ID)

X_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON = dcc.RadioItems(
    inline=True,
    id=X_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON_ID,
    labelStyle={"margin-left": "20px"}
)

Y_AXIS_GRAPH_3D_GRAPH = dcc.Graph(
    id=Y_AXIS_GRAPH_ID,
)

Y_AXIS_AMP_VAR_FOR_FREQ_GRAPH = dcc.Graph(id=Y_AXIS_AMP_VAR_FOR_FREQ_GRAPH_ID)

Y_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON = dcc.RadioItems(
    inline=True,
    id=Y_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON_ID,
    labelStyle={"margin-left": "20px"}
)

Y_AXIS_AREA_VAR_GRAPH = dcc.Graph(id=Y_AXIS_FFT_AREA_VAR_PLOT_ID)

Z_AXIS_GRAPH_3D_GRAPH = dcc.Graph(
    id=Z_AXIS_GRAPH_ID,
)

Z_AXIS_AMP_VAR_FOR_FREQ_GRAPH = dcc.Graph(id=Z_AXIS_AMP_VAR_FOR_FREQ_GRAPH_ID)

Z_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON = dcc.RadioItems(
    inline=True,
    id=Z_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON_ID,
    labelStyle={"margin-left": "20px"}
)

Z_AXIS_AREA_VAR_GRAPH = dcc.Graph(id=Z_AXIS_FFT_AREA_VAR_PLOT_ID)

ADD_FAILURE_FREQ_TRACE_INPUT_ID = "add-failure-freq-input"
ADD_FAILURE_FREQ_BTN_ID = "add-failure-freq-button"
ADD_FAILURE_FREQ_INPUT_DIV = html.Div(
    [
        html.P("Ingrese una frecuencia de fallo para marcar la traza"),
        dbc.Input(type="number", min=0, id=ADD_FAILURE_FREQ_TRACE_INPUT_ID),
    ]
)
ADD_FAILURE_FREQ_BTN = dbc.Button(
    id=ADD_FAILURE_FREQ_BTN_ID,
    children=["Añadir Traza"],
    n_clicks=0,
    color="secondary",
    className="me-1",
)


X_AXIS_GRAPH_TAB = dbc.Tab(
    dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    dbc.Col(
                        [
                            ADD_FAILURE_FREQ_INPUT_DIV,
                            html.Br(),
                            ADD_FAILURE_FREQ_BTN,
                        ],
                        width=2,
                    ),
                ),
                dbc.Col(X_AXIS_GRAPH_3D_GRAPH, width=10),
                X_AXIS_AREA_VAR_GRAPH,
                X_AXIS_AMP_VAR_FOR_FREQ_GRAPH,
                X_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON
            ]
        )
    ),
    id=X_AXIS_GRAPH_TAB_ID,
    label="Eje X",
)

Y_AXIS_GRAPH_TAB = dbc.Tab(
    dbc.Card(
        dbc.CardBody(
            [
                Y_AXIS_GRAPH_3D_GRAPH,
                Y_AXIS_AREA_VAR_GRAPH,
                Y_AXIS_AMP_VAR_FOR_FREQ_GRAPH,
                Y_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON
            ]
        )
    ),
    id=Y_AXIS_GRAPH_TAB_ID,
    label="Eje Y",
)


Z_AXIS_GRAPH_TAB = dbc.Tab(
    dbc.Card(
        dbc.CardBody(
            [
                Z_AXIS_GRAPH_3D_GRAPH,
                Z_AXIS_AREA_VAR_GRAPH,
                Z_AXIS_AMP_VAR_FOR_FREQ_GRAPH,
                Z_AXIS_AREA_VAR_OPTIONS_RADIO_BUTTON
            ]
        )
    ),
    id=Z_AXIS_GRAPH_TAB_ID,
    label="Eje Z",
)


GRAPHS_TITLE_DIV_ID = "graphs-title-div"
GRAPHS_TITLE_DIV = html.Div(
    id=GRAPHS_TITLE_DIV_ID
)
TRIDIMENSIONAL_GRAPHS_TABS = dbc.Spinner(
    [
        dmc.Divider(),
        html.Br(),
        GRAPHS_TITLE_DIV,
        dbc.Tabs(
            [X_AXIS_GRAPH_TAB, Y_AXIS_GRAPH_TAB, Z_AXIS_GRAPH_TAB],
            id=TRIDIMENSIONAL_GRAPHS_TABS_ID,
        )
    ],
    type="grow",
    color="primary",
    spinner_style={"position": "absolute", "left": "50%", "top": "50px"},
    delay_show=250,
)

layout_nested_div = html.Div(
    [div_view_title, data_selection_card_row, TRIDIMENSIONAL_GRAPHS_TABS],
    id="vibration-analysis-view-nested",
    style=VISIBILE_STYLE,
)

#####################################################
# Data Store components declaration to hold downloaded
# information.
#####################################################
vibration_store = dcc.Store(id="vibration-data", storage_type="session")


#####################################################
# Declaration of spinner to show load of view the first time
#####################################################
progress_views_transition_spinner = dbc.Spinner(
    color="primary",
    spinner_style=HIDDEN_STYLE,
    id="vibration-analysis-load-spinner",
    size="md",
)


layout = html.Div(
    [LOCATION_URL, layout_nested_div, vibration_store],
    id="vibration-analysis-view",
    style=CONTENT_STYLE,
)


#####################################################
# Dash Callbacks Declaration
# From here on, you'll see the declaration of callbacks
# that connect inputs/outputs based on the components
# declared above.
# https://dash.plotly.com/callback-gotchas
#####################################################
def _get_datetime_instances(date_start, date_end, start_time, end_time):
    # Create datetime objects from the string values
    start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
    end_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")

    # Join the date and time strings
    start_str = f"{date_start} {start_dt.time().replace(second=0)}"
    end_str = f"{date_end} {end_dt.time().replace(second=0)}"

    start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")

    # Set the timezone of the datetime objects to America/Denver
    timezone = pytz.timezone("America/Mexico_City")
    start_dt = timezone.localize(start_dt)
    end_dt = timezone.localize(end_dt)
    return start_dt, end_dt


@callback(
    Output(vibration_store, "data"),
    Output(TENANT_ID_INPUT_ID, "options"),
    Output(TENANT_ID_INPUT_ID, "value"),
    Output(MACHINE_ID_INPUT_ID, "options"),
    Output(MACHINE_ID_INPUT_ID, "value"),
    Output(VISUALIZATION_PERIOD_INPUT_ID, "options"),
    Output(VISUALIZATION_PERIOD_INPUT_ID, "value"),
    Output(SENSOR_TYPE_INPUT_KEY, "options"),
    Output(SENSOR_TYPE_INPUT_KEY, "value"),
    Output(
        TRIDIMENSIONAL_GRAPHS_TABS_ID, "children"
    ),  # We don't update. Only for spinner animation
    Output('vibration-analysis-url', "pathname"),
    Input(vibration_store, "data"),
    State("logged-in-status", "data"),
    background=True,
    manager=background_callback_manager,
)
def init_view_data(data, login_data):
    if not auth.validate_logged_in(login_data):
        return ([dash.no_update] * 10) + ["/login"]

    log.info("Trying to download information from remote server...")

    if data:
        log.info(f"Remote data is already locally saved in the session.")
        tenant_ids = ["heinz-001"]
        machines_id = {"heinz-001": list(["Motor_1", "Motor_3", "Motor_4"])}
        perceptions = ["VibrationAcceleration", "VibrationSpeed"]
        visualization_periods = ["Día Actual"]
        stored_data = {"vibration-analysis-downloaded": True}
        out_tuple = (
            stored_data,
            tenant_ids,
            tenant_ids[0],
            machines_id[tenant_ids[0]],
            machines_id[tenant_ids[0]][0],
            perceptions,
            perceptions[0],
            visualization_periods,
            visualization_periods[0],
            dash.no_update,
            dash.no_update
        )
        return out_tuple

    else:
        log.info(f"Pulling information from remote server started...")
        tenant_ids = ["heinz-001"]
        machines_id = {"heinz-001": list(["Motor_1", "Motor_3", "Motor_4"])}
        perceptions = ["VibrationAcceleration", "VibrationSpeed"]
        visualization_periods = ["Día Actual"]
        stored_data = {"vibration-analysis-downloaded": True}
        out_tuple = (
            stored_data,
            tenant_ids,
            tenant_ids[0],
            machines_id[tenant_ids[0]],
            machines_id[tenant_ids[0]][0],
            perceptions,
            perceptions[0],
            visualization_periods,
            visualization_periods[0],
            dash.no_update,
            dash.no_update
        )
        return out_tuple


@callback(
    Output(X_AXIS_GRAPH_3D_GRAPH, "figure"),
    Output(Y_AXIS_GRAPH_ID, "figure"),
    Output(Z_AXIS_GRAPH_ID, "figure"),
    Output(WRONG_INTERVAL_ALERT_ID, "hide"),
    Output(NO_DATA_FOUND_ALERT_ID, 'hide'),
    Output(GRAPHS_TITLE_DIV_ID, 'children'),
    Input(SHOW_DATA_BUTTON_ID, "n_clicks"),
    Input(ADD_FAILURE_FREQ_BTN_ID, "n_clicks"),
    State(TENANT_ID_INPUT_ID, "value"),
    State(MACHINE_ID_INPUT_ID, "value"),
    State(VISUALIZATION_PERIOD_INPUT_ID, "value"),
    State(SENSOR_TYPE_INPUT_KEY, "value"),
    State(X_AXIS_GRAPH_ID, "figure"),
    State(Y_AXIS_GRAPH_ID, "figure"),
    State(Z_AXIS_GRAPH_ID, "figure"),
    State(ADD_FAILURE_FREQ_TRACE_INPUT_ID, "value"),
    State(VIBRATION_INTERVAL_START_DATE_INPUT_ID, "value"),
    State(VIBRATION_INTERVAL_END_DATE_INPUT_ID, "value"),
    State(VIBRATION_INTERVAL_START_TIME_ID, "value"),
    State(VIBRATION_INTERVAL_END_TIME_ID, "value"),
    State(VIBRATION_INTERVAL_VISUALIZATION_DROPDOWN_ID, "value"),
    background=True,
    manager=background_callback_manager,
    prevent_initial_call=True,
    running=[(Output(SHOW_DATA_BUTTON_ID, "disabled"), True, False)],
)
def show_vibration_data_3d(
    n_clicks_1st,
    n_clicks_2nd,
    tenant_id,
    machine_id,
    visualization_period,
    perception_selected,
    figure_3d_x,
    figure_3d_y,
    figure_3d_z,
    failure_freq_value,
    start_date,
    end_date,
    start_time,
    end_time,
    interval_analysis_kind
):
    if ctx.triggered_id == SHOW_DATA_BUTTON_ID:
        logging.info("Donwloading data...")

        # TODO: Hard Validate the input ranges
        start_datetime, end_datetime = _get_datetime_instances(
            start_date, end_date, start_time, end_time
        )
        credentials = service_account.Credentials.from_service_account_file(
            auth.CREDENTIALS_PATH
        )

        bq = timeseries.BigQueryTimeSeries(credentials=credentials)

        time_series_interval = TimeSeriesInterval(
            start_datetime.timestamp() * 1e6,
            end_datetime.timestamp() * 1e6,
            "heinz-001",
            "Motor_1",
            "VibrationSpeed",
            columns=["signal", "observation_timestamp", "rpm"],
        )

        is_valid_interval = VibrationCascadeGraph.valid_interval_option(
            VibrationIntervalOption.from_readable(interval_analysis_kind),
            time_series_interval
        )

        if is_valid_interval:
            df = bq.get_metrics_dataframe(time_series_interval)

            graph = VibrationCascadeGraph(
                VibrationIntervalOption.from_readable(interval_analysis_kind),
                time_series_interval,
                df,
                machine_id,
                tenant_id,
            )

            plts = graph.get_fig()

            data_found = not df.empty

            data_interval_message = f"Data encontrada entre {time_series_interval.start_datetime} y {time_series_interval.end_datetime}"

            return plts[0], plts[1], plts[2], True, data_found, data_interval_message
        else:
            return dash.no_update, dash.no_update, dash.no_update, False, True, ""

    elif ctx.triggered_id == ADD_FAILURE_FREQ_BTN_ID:
        return (
            entities.add_vertical_3d_failure_freq(figure_3d_x, failure_freq_value),
            entities.add_vertical_3d_failure_freq(figure_3d_y, failure_freq_value),
            entities.add_vertical_3d_failure_freq(figure_3d_z, failure_freq_value),
            True,
            True,
            dash.no_update
        )


# REGISTER CALLBACK FOR CLICKED DATA ON CASCADE GRAPHS
for i in range(3):
    current_3d_plot_id = ALL_AXIS_CASCADE_GRAPHS_IDS[i]
    current_amp_var_for_freq_plot_id = ALL_AXIS_AMP_VAR_FOR_FREQ_IDS[i]
    current_area_plot = ALL_AXIS_AREA_VAR_IDS[i]
    current_amp_var_for_freq_radio_buttons = ALL_AXIS_AMP_VAR_FOR_FREQ_RADIO_BUTTONS[i]

    @callback(
        Output(current_amp_var_for_freq_radio_buttons, "options"),
        Output(current_amp_var_for_freq_radio_buttons, "value"),
        Input(current_3d_plot_id, "clickData"),
        State(current_3d_plot_id, "figure"),
        prevent_initial_call=True,
    )
    def show_valid_freqs_for_trace_click(clickData, figure):
        if "pointNumber" not in clickData["points"][0]:
            return dash.no_update, dash.no_update, dash.no_update  # The clicked was not in a signal

        # pointNumber is the array index of the clicked frequency
        x_freq_index = clickData["points"][0]["pointNumber"]
        plots = iter(figure["data"])
        scatter_data = next(plt for plt in plots if plt["customdata"][0] == entities.SIGNAL_TRACE_TYPE_VALUE)

        # Get the possible options to the left
        left_freqs_idx = [ i for i in range(x_freq_index-1, x_freq_index-6, -1) ]
        left_freqs_idx = list(filter( lambda idx: idx >= 0, left_freqs_idx ))
        right_freqs_idx = [ i for i in range(x_freq_index + 1, x_freq_index + 6, 1) ]
        right_freqs_idx = list(filter(lambda idx: idx < len(scatter_data["y"]), right_freqs_idx))
        left_freqs = list(map(
            lambda index: {"label": f"{scatter_data['y'][index]:.2f}", "value": index}, left_freqs_idx
        ))
        right_freqs = list(map(
            lambda index: {"label": f"{scatter_data['y'][index]:.2f}", "value": index}, right_freqs_idx
        ))
        left_freqs.reverse()
        cur_val = {"label": f"{scatter_data['y'][x_freq_index]:.2f}", "value": x_freq_index}
        radio_buttons_options = left_freqs + [cur_val] + right_freqs

        return radio_buttons_options, x_freq_index

    @callback(
        Output(current_amp_var_for_freq_plot_id, "figure"),
        Input(current_amp_var_for_freq_radio_buttons, 'value'),
        State(current_3d_plot_id, "figure"),
        prevent_initial_call=True
    )
    def show_amplitude_for_radio_button_freq(freq_index, figure):
        x_values = []  # dates
        y_values = []  # amplitude
        for scatter_data in figure["data"]:
            if scatter_data["customdata"][0] == entities.SIGNAL_TRACE_TYPE_VALUE:
                y_values.append(scatter_data["z"][freq_index])
                x_values.append(scatter_data["x"][freq_index])
        x_values.reverse()
        y_values.reverse()
        graph = entities.FrequencyAmplitudeVariationGraph(
            x_values, y_values, scatter_data["y"][freq_index]
        )
        return graph.get_fig()

    @callback(
        Output(current_area_plot, "figure"),
        Input(current_3d_plot_id, "figure"),
        State(current_3d_plot_id, "figure"),
        prevent_initial_call=True,
    )
    def show_area_variation_for_cascade_lines(clickData, figure):
        if figure is None:
            return dash.no_update
        x_values = []  # dates
        y_values = []  # amplitude
        for scatter_data in figure["data"]:
            if scatter_data["customdata"][0] == entities.SIGNAL_TRACE_TYPE_VALUE:
                area_value = trapz(scatter_data["z"], scatter_data["y"])
                x_values.append(scatter_data["x"][0])
                y_values.append(area_value)

        x_values.reverse()
        y_values.reverse()
        graph = entities.AreaVariationGraph(x_values, y_values)

        return graph.get_fig()


@callback(
    Output(VIBRATION_INTERVAL_START_TIME_ID, "disabled"),
    Output(VIBRATION_INTERVAL_END_TIME_ID, "disabled"),
    Input(VIBRATION_INTERVAL_VISUALIZATION_DROPDOWN_ID, "value"),
)
def enable_time_input(cur_analysis_type):
    cur_type_enum = VibrationIntervalOption.from_readable(cur_analysis_type)
    if cur_type_enum in {VibrationIntervalOption.FULL_DETAILED, VibrationIntervalOption.HOURLY_AVG}:
        return False, False
    else:
        return True, True
