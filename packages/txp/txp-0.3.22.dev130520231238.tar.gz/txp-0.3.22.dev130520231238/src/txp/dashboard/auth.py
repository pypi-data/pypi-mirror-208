"""
    This file contains the helper code to handle the
    Dash App authentication.

    Currently supports the local Credentials file usage.
"""
import os
import toml
import datetime
import logging

# TODO: This might be a problem. The logging configuration is being taken from `txp` package
from txp.common.config import settings

log = logging.getLogger(__name__)
log.setLevel(settings.txp.general_log_level)

#####################################################
# Credentials SETUP
# This setup should change for deployed application.
# If deployed inside GCP, then authentication is transparent for client libs.
#####################################################
# CREDENTIALS SETUP
script_path = os.path.realpath(__file__)
root_path = os.path.dirname(script_path)
common_path = os.path.join(os.path.dirname(root_path), "common")
CREDENTIALS_PATH = os.path.join(
    os.path.join(common_path, "credentials"), "pub_sub_to_bigquery_credentials.json"
)


####################################################
# GCP values to perform identity platform authentication
####################################################
GCP_FIREBASE_FILE = f"{root_path}/auth.toml"
with open(GCP_FIREBASE_FILE, "r") as f:
    AUTH_CONFIG = toml.load(f)

CLIENT_OAUTH_SECRET = AUTH_CONFIG["oauth_secrets"]
FIREBASE_API_KEY = AUTH_CONFIG["firebase_api_key"]
GOOGLE_OAUTH_REDIRECT = AUTH_CONFIG["oauth_redirect_url"]
FIREBASE_DEFAULT_SERVICE_ACCOUNT = AUTH_CONFIG[
    "firebase_default_service_account"
]


#####################################################
# Helper fucntion for sibling pages to validate if the user
# is logged-in or not
#####################################################
_EXPIRATION_LOGGED_IN_INTERVAL_SECS = 604800


def validate_logged_in(logged_in_data) -> bool:
    if not logged_in_data:
        return False
    if not logged_in_data['logged-in']:
        log.info("The user is not logged-in.")
        return False
    # At this point we'll check if the logged-in expired
    login_datetime = logged_in_data.get('since')
    login_datetime = datetime.datetime.fromtimestamp(login_datetime)

    if (datetime.datetime.now() - login_datetime).total_seconds() > _EXPIRATION_LOGGED_IN_INTERVAL_SECS:  # 604800 secs in a week
        logging.info(f"User logged in status has expired. Re-login is required")
        logged_in_data.update({'logged-in': False})  # Deactivates the valid logged in
        return False

    else:
        logging.info(f"User logged in status is still valid")
        return True

