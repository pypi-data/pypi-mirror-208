import dash_bootstrap_components as dbc
import urllib.parse
from dash import (
    Input,
    Output,
    State,
    dcc,
    html,
    callback,
    DiskcacheManager,
    ctx,
)
import dash
from google.oauth2 import service_account
from txp.common.models import (
    ProjectFirestoreModel,
    get_assets_metrics,
    AssetMetrics,
)
import txp.common.timeseries as timeseries
from txp.common.timeseries import TimeSeriesInterval
from txp.dashboard.pages.styles import *
import txp.dashboard.auth as auth
import logging

# TODO: This might be a problem. The logging configuration is being taken from `txp` package
from txp.common.config import settings

log = logging.getLogger(__name__)
log.setLevel(settings.txp.general_log_level)

dash.register_page(__name__, path="/asset-details")


#####################################################
# Backend cache for long running callbacks. We configure the local recommended.
# More info here: https://dash.plotly.com/background-callbacks
#####################################################
import diskcache

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)


######################################################
# Dummy component to trigger init callback of the page
######################################################
INIT_CALLBACK_DUMMY_COMPONENT_ID = "dummy-component"
init_callback_dummy_component = html.Div(
    "I'm dummy", id=INIT_CALLBACK_DUMMY_COMPONENT_ID, style={"visibility": "hidden"}
)


#####################################################
# Dash Components Declaration
# From here on, you'll see the declaration of components shown in the
# General Dashboard.
# Components that requires input values to render, will be setup
# with the helper function "init_view_components"
#####################################################
#####################################################
# Page Header Declaration
#####################################################
PAGE_HEADER = html.Div(
    children=[
        html.H1("Detalles de Máquina"),
        html.Br(),  # let a space in the vertical layout
    ]
)


#####################################################
# Declaration of Location element to handle query params
#####################################################
LOCATION_URL = dcc.Location(id="url", refresh=True)


#####################################################
# Declaration of view layout elements
#####################################################

ASSET_CARD_ASSET_ID = "asset-card-asset-id"
ASSET_CARD_LAST_SEEN_ID = "asset-card-last-seen"
ASSET_CARD_METRIC_TEMPERATURE_ID = "asset-card-metric-temperature"
ASSET_CARD_METRIC_RPM_ID = "asset-card-metric-rpm"
ASSET_CARD_METRIC_WORKED_TIME_ID = "asset-card-metric-worked-time"


TITLE_DIV = html.H1("Detalles de Equipo")

ASSETS_GROUP_SELECTBOX_ID = "assets-group-select"
ASSETS_GROUP_SELECTBOX = dcc.Dropdown([], id=ASSETS_GROUP_SELECTBOX_ID, clearable=False)

ASSET_SELECTBOX_ID = "asset-select"
ASSET_SELECTBOX = dcc.Dropdown([], id=ASSET_SELECTBOX_ID, clearable=False)

SEE_DETAILS_BTN_ID = "see-details-btn"
SEE_DETAILS_BTN = dbc.Button(
    "Ver Detalles", outline=True, color="primary", id=SEE_DETAILS_BTN_ID
)

ASSET_CARD_ASSET_TR_ID = html.Tr(
    [html.Td("Equipo"), html.Td("No Disponible", id=ASSET_CARD_ASSET_ID)]
)

ASSET_CARD_LAST_SEEN_TR_ID = html.Tr(
    [
        html.Td("Visto por última vez"),
        html.Td("No Disponible", id=ASSET_CARD_LAST_SEEN_ID),
    ]
)

ASSET_CARD_INFO_TABLE = dbc.Table(
    [html.Tbody([ASSET_CARD_ASSET_TR_ID, ASSET_CARD_LAST_SEEN_TR_ID])], bordered=True
)

ASSET_CARD_METRIC_TEMPERATURE_DIV = html.Div(
    [
        dbc.Card(
            [
                dbc.CardHeader(
                    "Temperatura",
                    className="card-title",
                    style={"font-weight": "bold"},
                ),
                dbc.CardBody(
                    html.Div(
                        "No hay data para mostrar",
                        id=ASSET_CARD_METRIC_TEMPERATURE_ID,
                        style={"font-size": "22px", "color": "green"},
                    )
                ),
            ]
        )
    ]
)

ASSET_CARD_METRIC_RPM_DIV = html.Div(
    [
        dbc.Card(
            [
                dbc.CardHeader(
                    "Velocidad",
                    className="card-title",
                    style={"font-weight": "bold"},
                ),
                dbc.CardBody(
                    html.Div(
                        "No hay data para mostrar",
                        id=ASSET_CARD_METRIC_RPM_ID,
                        style={"font-size": "22px", "color": "green"},
                    )
                ),
            ]
        )
    ]
)

ASSET_CARD_METRIC_WORKED_TIME_DIV = html.Div(
    [
        dbc.Card(
            [
                dbc.CardHeader(
                    "Horas Encendido",
                    className="card-title",
                    style={"font-weight": "bold"},
                ),
                dbc.CardBody(
                    html.Div(
                        "No hay data para mostrar",
                        id=ASSET_CARD_METRIC_WORKED_TIME_ID,
                        style={"font-size": "22px", "color": "green"},
                    )
                ),
            ]
        )
    ]
)

# Declaration of component for the temperature chart
TEMPERATURE_CHART_COMPONENT_ID = "asset-temperature-chart"
TEMPERATURE_CHART_COMPONENT = dcc.Graph(id=TEMPERATURE_CHART_COMPONENT_ID)

# Declaration of component for the RPM chart
RPM_CHART_COMPONENT_ID = "asset-rpm-chart"
RPM_CHART_COMPONENT = dcc.Graph(id=RPM_CHART_COMPONENT_ID)

ASSET_CARD_CONTAINER = dbc.Spinner(
    [
        dbc.Row(
            [
                dbc.Col(ASSETS_GROUP_SELECTBOX, width=6),
                dbc.Col(ASSET_SELECTBOX, width=6),
            ]
        ),
        html.Br(),
        dbc.Row([dbc.Col(ASSET_CARD_INFO_TABLE)]),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(ASSET_CARD_METRIC_TEMPERATURE_DIV),
                dbc.Col(ASSET_CARD_METRIC_RPM_DIV),
                dbc.Col(ASSET_CARD_METRIC_WORKED_TIME_DIV),
            ]
        ),
        html.Br(),
    ],
    type="grow",
    color="primary",
    spinner_style={"position": "absolute", "left": "50%", "top": "50px"},
)

ASSET_TIMESERIES_CONTAINER_ID = "assets-timeseries-chart"
ASSET_TIMESERIES_LOADING_TEXT_ID = "timeseries-loading-text"
ASSET_TIMESERIES_PLOTS_ID = "timeseries-plottes-grid"
ASSET_TIMESERIES_CONTAINER = dbc.Spinner(
    [
        dbc.Row(
            html.P(
                children="La carga de gráficos con la versión Premium "
                "es más rápida..."
            ),
            style={"visibility": "hidden"},
            id=ASSET_TIMESERIES_LOADING_TEXT_ID,
        ),
        dbc.Row(
            [
                dbc.Col(TEMPERATURE_CHART_COMPONENT, width=6),
                dbc.Col(RPM_CHART_COMPONENT, width=6),
            ],
            id=ASSET_TIMESERIES_PLOTS_ID,
        ),
    ],
    type="grow",
    color="primary",
    spinner_style={"position": "absolute", "left": "50%", "top": "50px"},
    id=ASSET_TIMESERIES_CONTAINER_ID,
)


######################################################
# Dummy component to trigger init callback of the page
######################################################
INIT_CALLBACK_DUMMY_COMPONENT_ID = "dummy-details-component"
DUMMY_DETAILS_COMPONENTS = html.Div(
    "I'm dummy", id=INIT_CALLBACK_DUMMY_COMPONENT_ID, style={"visibility": "hidden"}
)


layout = html.Div(
    [
        LOCATION_URL,
        DUMMY_DETAILS_COMPONENTS,
        TITLE_DIV,
        html.Br(),
        ASSET_CARD_CONTAINER,
        ASSET_TIMESERIES_CONTAINER,
    ],
    style=CONTENT_STYLE,
)


#####################################################
# Dash Callbacks Declaration
# set_machines_group
#
# Input 'url.search': Parse the possible url search values for asset details and
# assign those values to the appropriated select boxes
#####################################################
@callback(
    Output(ASSETS_GROUP_SELECTBOX_ID, "options"),
    Output(ASSET_SELECTBOX_ID, "options"),
    Output(ASSETS_GROUP_SELECTBOX_ID, "value"),
    Output(ASSET_SELECTBOX_ID, "value"),
    Input("url", "search"),
    State("project-model-snapshot", "data"),
    State("logged-in-status", "data"),
)
def set_select_values(
    url_search,
    data,
    login_data
):
    if not auth.validate_logged_in(login_data):
        return ["/login"] + [dash.no_update * 4]

    # Parses project model in memory
    project_model: ProjectFirestoreModel = ProjectFirestoreModel.from_dict(
        data["project-model"]
    )

    if ctx.triggered_id == "url" or url_search:  # Parses the URL search params
        params = urllib.parse.parse_qs(url_search[1:])
        asset_id = params.get("asset", [""])[0]
        assets_group = params.get("group", [""])[0]
        group_options = list(project_model.assets_groups_table.keys())
        assets_options = project_model.assets_groups_table[assets_group].assets
        return group_options, assets_options, assets_group, asset_id

    group = project_model.assets_groups[0].name
    assets = project_model.assets_groups_table[group].assets
    return list(project_model.assets_groups_table.keys()), assets, group, assets[0]

#####################################################
# Dash Callbacks Declaration
# update_assets_options
#
# To be executed when the assets_group dropdown value changes
####################################################
@callback(
    Output(ASSET_SELECTBOX_ID, "options", allow_duplicate=True),
    Output(ASSET_SELECTBOX_ID, "value", allow_duplicate=True),
    Input(ASSETS_GROUP_SELECTBOX_ID, "value"),
    State("project-model-snapshot", "data"),
    prevent_initial_call=True
)
def update_assets_dropdown(group_value, data):
    project_model: ProjectFirestoreModel = ProjectFirestoreModel.from_dict(
        data["project-model"]
    )
    options = project_model.assets_groups_table[group_value].assets
    return options, options[0]


#####################################################
# Callback definition to render the resume tables for the asset
#####################################################
@callback(
    Output(ASSET_CARD_ASSET_ID, "children"),
    Output(ASSET_CARD_LAST_SEEN_ID, "children"),
    Output(ASSET_CARD_METRIC_TEMPERATURE_ID, "children"),
    Output(ASSET_CARD_METRIC_RPM_ID, "children"),
    Output(ASSET_CARD_METRIC_WORKED_TIME_ID, "children"),
    Input(ASSET_SELECTBOX_ID, 'value'),
    State(ASSETS_GROUP_SELECTBOX_ID, 'value'),
    background=True,
    manager=background_callback_manager,
    running=[
        (
            Output(ASSET_TIMESERIES_PLOTS_ID, 'style'),
            {'visibility': "hidden"},
            {'visibility': "visible"},
         )
    ]
)
def render_asset_metrics(asset_id, assets_group_id):
    credentials = service_account.Credentials.from_service_account_file(
        auth.CREDENTIALS_PATH
    )
    metric: AssetMetrics = get_assets_metrics(
        credentials, [asset_id], "gao-001"
    )[0]
    return (
        f"{metric.asset_id}",
        f"{metric.last_seen}",
        f"{metric.temperature:.2f} C",
        f"{metric.rpm:.2f} RPM",
        f"{metric.worked_hours:.2f} Hrs"
    )


##############################################################################
# Define the callback to generate the Temperature chart for the asset
# Invocation: The callback executes when the metric Temperature is updated
# Runtime: Database network total trip access.
##############################################################################
@callback(
    Output(TEMPERATURE_CHART_COMPONENT_ID, 'figure'),
    Output(RPM_CHART_COMPONENT_ID, 'figure'),
    Input(ASSET_CARD_METRIC_TEMPERATURE_ID, 'children'),
    State(ASSET_SELECTBOX_ID, 'value'),
    State("project-model-snapshot", "data"),
    background=True,
    manager=background_callback_manager,
    running=[
        (
                Output(ASSET_TIMESERIES_PLOTS_ID, 'style'),
                {'visibility': "hidden"},
                {'visibility': "visible"},
        )
    ]
)
def render_metrics_chart(temperature_metric, asset_id, data):
    if asset_id is None:
        project_model: ProjectFirestoreModel = ProjectFirestoreModel.from_dict(
            data["project-model"]
        )
        asset_id = project_model.assets_groups[0].assets[0]

    start, end = timeseries.get_last_hour_interval()
    time_series_interval = TimeSeriesInterval(
        start,
        end,
        'gao-001',
        asset_id,
        "VibrationSpeed",
        columns=["observation_timestamp", "temperature", "rpm"]
    )
    credentials = service_account.Credentials.from_service_account_file(
        auth.CREDENTIALS_PATH
    )
    bq = timeseries.BigQueryTimeSeries(
        credentials=credentials
    )
    df = bq.get_metrics_dataframe(time_series_interval)
    temperature_ts = timeseries.TemperatureChart(
        time_series_interval,
        df
    )
    rpm_ts = timeseries.RpmChart(time_series_interval, df)
    return temperature_ts.get_plot(), rpm_ts.get_plot()
