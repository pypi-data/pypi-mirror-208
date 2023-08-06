import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, callback, DiskcacheManager
import dash
# TODO: This might be a problem. The logging configuration is being taken from `txp` package
from txp.common.config import settings
from txp.common.utils.authentication_utils import get_google_oauth_flow, sing_in_user_in_identity_platform, \
    get_principal_credentials, AuthenticationInfo
import urllib.parse
import logging
from txp.dashboard.auth import *
import datetime
import oauthlib
log = logging.getLogger(__name__)
log.setLevel(settings.txp.general_log_level)


dash.register_page(__name__, path="/login")

####################################################
# GENERATE AUTHENTICATION FLOW LINK
###################################################
_auth_flow = get_google_oauth_flow(
    client_oauth_secret=CLIENT_OAUTH_SECRET,
    redirect_url=GOOGLE_OAUTH_REDIRECT,
)


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
LOCATION_URL = dcc.Location(id='login-url', refresh=True)


layout = html.Div(
    [
        LOCATION_URL,
        html.Div(
            [
                html.Div(
                    [
                        html.H2("Ingresar a Tranxpert", className="card-title"),
                        html.Br(),
                        html.A(
                            "Ingresar con Google",
                            href=_auth_flow.authorization_url()[0],
                            className="btn btn-primary",
                            id="google-login-button",
                        ),
                        html.Br(),
                        dbc.Spinner(
                            delay_hide=.3,
                            id="google-login-spin",
                            spinner_style={"visibility": "hidden"}
                        )
                    ],
                    className="card-body",
                )
            ],
            className="card",
            style={"width": "50%", "margin": "auto", "marginTop": "15%"},
        )
    ],
    style={"position": "fixed", "top": 0, "bottom": 0, "left": 0, "right": 0, "backgroundColor": "rgba(255, 255, 255, 0.95)"},
)


#####################################################
# Dash Callbacks Declaration
# From here on, you'll see the declaration of callbacks
# that connect inputs/outputs based on the components
# declared above.
# https://dash.plotly.com/callback-gotchas
#####################################################
@callback(
    Output('login-url', 'search'),
    Output('login-url', 'pathname'),
    Output('logged-in-status', 'data'),
    Input('login-url', 'search'),
    State('logged-in-status', 'data'),
    background=True,
    manager=background_callback_manager,
    running=[
        (Output("google-login-button", "style"), {'visibility': 'hidden'}, {'visibility': 'visible'}),
        (Output("google-login-spin", "style"), {"visibility": "visible"}, {"visibility": "hidden"})
    ]
)
def _is_auth_redirection(search, data):
    if validate_logged_in(data):
        log.info("The user is logged-in. Go to home")
        return "", "", data

    if not search:
        return  dash.no_update, dash.no_update, dash.no_update

    params = urllib.parse.parse_qs(search[1:])
    auth_code = params.get('code', [''])[0]

    try:
        identity_platform_credentials = sing_in_user_in_identity_platform(
            auth_code,
            FIREBASE_API_KEY,
            CLIENT_OAUTH_SECRET,
            GOOGLE_OAUTH_REDIRECT
        )
    except oauthlib.oauth2.rfc6749.errors.InvalidGrantError:
        log.error("Could not sign-in user in Identity Platform")
        return "", dash.no_update, dash.no_update

    if not identity_platform_credentials:
        log.error("Could not sign-in user in Identity Platform")
        return "", dash.no_update, dash.no_update

    role_credentials, role_enum = get_principal_credentials(
        identity_platform_credentials["email"],
        CLIENT_OAUTH_SECRET,
        identity_platform_credentials["idToken"],
        FIREBASE_DEFAULT_SERVICE_ACCOUNT
    )

    if not role_credentials:
        log.error(
            "Could not obtain Role Service Account credentials from Firestore"
        )
        return "", dash.no_update, dash.no_update

    log.info(
        f"Successfully authenticated user with email: "
        f"{identity_platform_credentials['email']}"
    )

    data = {
        "logged-in": True,
        "since": datetime.datetime.now().timestamp(),
        "user-role": role_enum.value
    }

    return "", "", data
