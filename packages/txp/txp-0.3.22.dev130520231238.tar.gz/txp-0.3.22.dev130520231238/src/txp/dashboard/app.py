"""
    This is the Dash application for Tranxpert UI based.

    The Web Application Dashboard is composed by a Sidebar that's acts as the
        navigation mechanisms between the views.

    Each individual View is contained on it's own file under the
    `pages` folder. Learn more: https://dash.plotly.com/urls#dash-pages
"""
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, DiskcacheManager, Dash, Output, Input, State
from google.oauth2 import service_account
from txp.common.models import ProjectFirestoreModel, get_project_model, models_pb2
from txp.common.utils.authentication_utils import AuthenticationInfo
from txp.dashboard import auth
from txp.dashboard.pages.styles import *
import logging
# TODO: This might be a problem. The logging configuration is being taken from `txp` package
from txp.common.config import settings
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
# Dash Components Declaration
# From here on, you'll see the declaration of components
# that are used across the app in different views.
#####################################################
#####################################################
# Sidebar Declaration
#####################################################


SIDEBAR_NAVIGATION_ELEMENT_ID = "sidebar-navigation-elems"
VIBRATION_ANALYSIS_LINK = "vibration-nav-btn"
sidebar = html.Div(
    [],
    style=SIDEBAR_STYLE,
    id="app-sidebar"
)

#####################################################
# Data Store components declaration to hold downloaded
# information.
#####################################################
project_model_store = dcc.Store(id="project-model-snapshot", storage_type="session")
logged_in_status = dcc.Store(id='logged-in-status', storage_type="local")

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SIMPLEX])
server = app.server
app.layout = html.Div([
	sidebar,
    project_model_store,
    logged_in_status,
	dash.page_container
])


#####################################################
# Dash Callbacks Declaration
# hide_vibration_analysis_if_role
# Checks it the user is logged-in. If it's logged, then
# shows the appropriate buttons in sidebar.
#####################################################
@app.callback(
    Output('app-sidebar', 'children'),
    Input('logged-in-status', 'data')
)
def hide_vibration_analysis_if_role(data):
    if not data:
        return []
    else:
        if AuthenticationInfo.UserRole(data['user-role']) == AuthenticationInfo.UserRole.Analyst:
            dash.page_registry['pages.home']['path'] = '/home'
            # Edit vibration analysis path
            dash.page_registry['pages.vibration_analysis']['path'] = '/'
            return [
                html.H1("Tranxpert"),
                html.Hr(),
                dbc.Nav(
                    [
                        dbc.NavLink(
                            "Análisis de Vibraciones",
                            href="/",
                            active="exact",
                            id=VIBRATION_ANALYSIS_LINK,
                            n_clicks=0,
                        ),
                    ],
                    vertical=True,
                    pills=True,
                    id=SIDEBAR_NAVIGATION_ELEMENT_ID
                ),
            ]

        else:
            return [
                html.H1("Tranxpert"),
                html.Hr(),
                dbc.Nav(
                    [
                        dbc.NavLink("Resumen", href="/", active="exact", id='inicio-nav-btn', n_clicks=0),
                        dbc.NavLink(
                            "Detalles de Equipo",
                            href="/asset-details",
                            active="exact",
                            id='asset-details-btn',
                            n_clicks=0,
                        )
                    ],
                    vertical=True,
                    pills=True,
                    id=SIDEBAR_NAVIGATION_ELEMENT_ID
                ),
            ]


#####################################################
# Dash Callbacks Declaration
# download_project_data
# After the use has been authenticated for the current tab,
# donwload the project model if the info is not found locally.
#####################################################
def _download_project_model() -> ProjectFirestoreModel:
    credentials = service_account.Credentials.from_service_account_file(
        auth.CREDENTIALS_PATH
    )

    project_model = get_project_model(
        credentials,
        [models_pb2.ALWAYS_REQUIRED, models_pb2.IOT_DEVICES_REQUIRED],
        "gao-001",
    )

    return project_model


@app.callback(
    Output("project-model-snapshot", "data"),
    Input('logged-in-status', 'data'),
    State("project-model-snapshot", "data"),
)
def download_project_data(logged_in_data, project_data):
    if not auth.validate_logged_in(logged_in_data):
        log.info("Unable to validate auth info for downloading project data")
        return dash.no_update

    if not project_data:
        project_data = {}
        logging.info("Local project data not found, connecting to remote DB")
        project_model = _download_project_model()
        if project_model:
            project_data.update({"project-model": project_model.get_dict()})
        return project_data

    logging.info("Project data model already in store")
    return project_data


if __name__ == '__main__':
    app.run_server(debug=True)

