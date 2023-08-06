import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, dash_table, callback, DiskcacheManager
import dash_mantine_components as dmc
import pandas as pd
import dash
from google.oauth2 import service_account
from txp.common.models import (
    ProjectFirestoreModel,
    get_project_model,
    models_pb2,
    get_assets_metrics,
)
from txp.dashboard.pages.styles import *
import txp.dashboard.auth as auth
import logging
# TODO: This might be a problem. The logging configuration is being taken from `txp` package
from txp.common.config import settings

log = logging.getLogger(__name__)
log.setLevel(settings.txp.general_log_level)

dash.register_page(__name__, path="/")

#####################################################
# Backend cache for long running callbacks. We configure the local recommended.
# More info here: https://dash.plotly.com/background-callbacks
#####################################################
import diskcache

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

####################################################
# DECLARE LINK COMPONENT TO INSPECT LINK ADDRESS
# SEARCHING AUTH RESPONSE
###################################################
LOCATION_URL = dcc.Location(id='home-url', refresh=True)

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
        html.H1("Resumen de monitoreo"),
        html.Br(),  # let a space in the vertical layout
    ]
)

#####################################################
# Asset Groups Resume table declaration
#####################################################
ASSETS_GROUPS_RESUME_TABLE_CONTAINER_ID = "assets-groups-resume-table-container"
ASSETS_GROUPS_TABLE_ID = "assets-groups-resume-table"
CONTENT_LAYOUT_ID = "main-content"

ASSETS_GROUPS_CONTAINER = dbc.Spinner(
    dbc.Card(
        [
            dbc.CardHeader(
                "Lineas Monitoreadas",
                className="card-title",
                style={"font-weight": "bold"},
            ),
            dbc.CardBody(
                [
                    dash_table.DataTable(
                        [],
                        style_cell={"textAlign": "center"},
                        cell_selectable=False,
                        id=ASSETS_GROUPS_TABLE_ID,
                    )
                ]
            ),
        ]
    ),
    type="grow",
    color="primary",
    spinner_style={"position": "absolute", "left": "50%", "top": "50px"},
)

#####################################################
# <br> tags for vertical spacing
#####################################################
DIVIDER_BRS_1 = html.Div([html.Br()] * 2)
DIVIDER_BRS_2 = html.Div([html.Br()] * 2)

#####################################################
# Declare a Divider to illustrate action
#####################################################
DIVIDER = dmc.Divider(
    variant="solid", labelPosition="center", label="Detalles de línea", size="xl"
)

#####################################################
# Declare the section for showing details of an asset
#####################################################
# Dropdown to select the line to show details from
ASSET_GROUP_SELECTION_DROPDOWN_ID = "line-selection-dropdown"
ASSET_GROUP_DROPDOWN = dcc.Dropdown(
    placeholder="Línea",
    options=[],
    value="",
    id=ASSET_GROUP_SELECTION_DROPDOWN_ID,
    clearable=False,
)

# Metrics organized as bootstrap columns
LINE_TOTAL_ASSETS_METRIC_ID = "total-assets-metric"
LINE_TOTAL_ASSETS_METRIC_DIV = html.Div(
    [
        dbc.Card(
            [
                dbc.CardHeader(
                    "Número de Equipos",
                    className="card-title",
                    style={"font-weight": "bold"},
                ),
                dbc.CardBody(
                    html.Div(
                        "No hay data para mostrar",
                        id=LINE_TOTAL_ASSETS_METRIC_ID,
                        style={"font-size": "20px", "color": "green"},
                    ),
                )
            ]
        )
    ],
)

LINE_CONNECTION_METRIC_ID = "line-connection-metric"
LINE_CONNECTION_METRIC_DIV = html.Div(
    [
        dbc.Card(
            [
                dbc.CardHeader(
                    "Connectividad",
                    className="card-title",
                    style={"font-weight": "bold"},
                ),
                dbc.CardBody(
                    html.Div(
                        "No hay data para mostrar",
                        LINE_CONNECTION_METRIC_ID,
                        style={"font-size": "22px", "color": "green"},
                    )
                )
            ]
        )
    ]
)

# Line Details Table
LINE_DETAILS_TABLE_COMPONENT_ID = "line-details-table-component"

LINE_DETAILS_TABLE_COMPONENT = dash_table.DataTable(
    [],
    columns=[
        {'name': 'Equipo', 'id': '1', 'type': 'text', 'presentation': 'markdown'},
        {'name': 'Temperatura', 'id': '2'},
        {'name': 'Velocidad', 'id': '3'},
        {'name': 'Horas Trabajadas', 'id': '4'},
        {'name': 'Visto por última vez', 'id': '5'}
    ],
    style_cell={"textAlign": "center"},
    cell_selectable=False,
    id=LINE_DETAILS_TABLE_COMPONENT_ID,
    css=[dict(selector="p", rule="margin: 0; text-align: center")],
    markdown_options={'link_target': '_self'}
)

LINE_DETAILS_TABLE_ROW = dbc.Spinner(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(LINE_TOTAL_ASSETS_METRIC_DIV, width=4),
                        ]
                    ),
                    html.Br(),
                    dbc.Row([dbc.Col(LINE_DETAILS_TABLE_COMPONENT)]),
                ]
            ),
        )
    ],
    type="grow",
    color="primary",
    spinner_style={"position": "absolute", "left": "50%", "top": "50px"},
)

LINE_DETAILS_ROW_ID = "line-details-row-section"
LINE_DETAILS_ROW = html.Div(
    [
        dbc.Row(
            DIVIDER
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div("Seleccione Línea: "),
                        ASSET_GROUP_DROPDOWN,
                    ],
                    width="6",
                )
            ],
            justify="between",
        ),
        html.Br(),
        LINE_DETAILS_TABLE_ROW,
    ],
    id=LINE_DETAILS_ROW_ID,
)

##############################################################
# Declaration of layout
##############################################################

layout = html.Div(
    [
        LOCATION_URL,
        PAGE_HEADER,
        ASSETS_GROUPS_CONTAINER,
        DIVIDER_BRS_1,
        LINE_DETAILS_ROW,
        init_callback_dummy_component,
    ],
    id=CONTENT_LAYOUT_ID,
    style=CONTENT_STYLE,
)


#####################################################
# Dash Callbacks Declaration
# From here on, you'll see the declaration of callbacks
# that connect inputs/outputs based on the components
# declared above.
# https://dash.plotly.com/callback-gotchas
#####################################################
def get_machine_link(l):
    href = f'/asset-details?asset={l[0]}&group={l[1].replace(" ", "%20")}'
    text = l[0]
    return f'[{text}]({href})'


def get_assets_groups_df(pm: ProjectFirestoreModel) -> pd.DataFrame:
    groups_names = list(map(lambda ag: ag.name, pm.assets_groups))

    num_of_assets = list(
        map(lambda group: len(pm.assets_groups_table[group].assets), groups_names)
    )

    lines_df = pd.DataFrame(
        {
            "Línea": groups_names,
            "Cantidad Equipos": num_of_assets,
        }
    )

    return lines_df


@callback(
    Output(ASSETS_GROUPS_TABLE_ID, "data"),
    Output("home-url", "pathname"),
    Input("project-model-snapshot", "data"),
    State("logged-in-status", "data"),
    background=True,
    manager=background_callback_manager,
    running=[
        (
                Output(LINE_DETAILS_ROW_ID, "style"),
                {"visibility": "hidden"},
                {"visibility": "visible"},
        ),
    ]
)
def init_view_data(data, login_data):
    # TODO: Donwload info from Firestore and render the table with that info
    if not auth.validate_logged_in(login_data):
        return dash.no_update, "/login"

    logging.info("Reading project model from local store")
    project_model: ProjectFirestoreModel = ProjectFirestoreModel.from_dict(
        data["project-model"]
    )

    assets_groups_dataframe = get_assets_groups_df(project_model)

    return assets_groups_dataframe.to_dict("records"), dash.no_update


@callback(
    Output(ASSET_GROUP_SELECTION_DROPDOWN_ID, "options"),
    Output(ASSET_GROUP_SELECTION_DROPDOWN_ID, "value"),
    Input(ASSETS_GROUPS_TABLE_ID, "data"),
    background=True,
    manager=background_callback_manager,
    prevent_initial_call=True
)
def set_line_details_dropdown_items(data):
    # TODO: when datasource changes, update select box
    options = list(map(lambda d: d["Línea"], data))
    return options, options[0]


@callback(
    Output(LINE_DETAILS_TABLE_COMPONENT_ID, "data"),
    Output(LINE_TOTAL_ASSETS_METRIC_ID, "children"),
    Input(ASSET_GROUP_SELECTION_DROPDOWN_ID, "value"),
    State("project-model-snapshot", "data"),
    background=True,
    manager=background_callback_manager,
    prevent_initial_call=True
)
def update_line_details_table(value, data):
    project_model: ProjectFirestoreModel = ProjectFirestoreModel.from_dict(
        data["project-model"]
    )
    assets = project_model.assets_groups_table[value].assets
    credentials = service_account.Credentials.from_service_account_file(
        auth.CREDENTIALS_PATH
    )
    metrics = get_assets_metrics(credentials, assets, "gao-001")
    rows = []
    for metric in metrics:
        d = {
            "1": get_machine_link([metric.asset_id, value]),
            "2": f"{metric.temperature} ºC",
            "3": f"{metric.rpm} RPM",
            "4": f"{metric.worked_hours}",
            "5": metric.last_seen,
        }
        rows.append(d)

    return rows, len(assets)
