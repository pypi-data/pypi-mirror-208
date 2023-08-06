import requests
import json
from google_auth_oauthlib.flow import Flow

# credentials
# GCLOUD configuration
# This values will configure everything required to interact with the GCP services and platform, regarding
# permissions and security
oauth_secrets="""{"web":{"client_id":"977520001763-0rom1eoqv26nso4qv1a9mvpdrnt1mu6q.apps.googleusercontent.com","project_id":"tranxpert-mvp","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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","redirect_uris":["https://tranxpert-mvp.firebaseapp.com/__/auth/handler","http://localhost:8501"],"javascript_origins":["http://localhost","http://localhost:5000","https://tranxpert-mvp.firebaseapp.com"]}}"""
firebase_api_key="""AIzaSyDE3qSVJKQc70O93yo5aGcmkyb1lfbG46g"""
oauth_redirect_url="""http://localhost:8502"""
firebase_default_service_account='{"type": "service_account", "project_id": "tranxpert-mvp", "private_key_id": "e5c67763e0832ca53374c5eca05d0d1c8f9ed9b7", "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCf9PuualOWTrU3\nmNEAbrWpw7ZrM8c8ztxdoBgKKiZzLppKFuQLigGp2KaTFvESoJBt9OVb6L+H+LMl\nhnaaty2Mn7aHPYEzk4+e+8ocdJe9qqflTsWQjnUxNSHNiIJnQ4AfC5U55w8Qys4x\n8/U1HCk6BqCmjYtIqynG+ruIuUYfgwBQPur3k9Lj0b/Z7f1tBa/T4x31SbMhcRa/\n9EJy7+vdbMo1WA7+QfamhSYB2SvNfXjokE9AZenfZSwV4SUfgVnOjSrqiMuyLzeK\n0Uv0IKEtLcrPLR3K2vExPMVp+WjLVntxmpOWeSdGpr2xheARKGn4pKg0u+bc8S5s\nX6w9Pk0vAgMBAAECggEASBxgbjPe9O8MwUCyUDiYyyzBCzkvg9lZ/RdUXxi7dse2\npNoG+rC/qTtTdRItohEiq39w+utFlV3oHW2uAHe+IBxMZFG08nR+ldS7O/LQCaBq\nynSlmlKuwH1MfOUirL0AgH5vSshAwXg8Vsa9b7D/YPpl6E/9T8hiMCMO8kdcNo3Y\n2oIpfoR8lG0hqTs3bvc+iFNAY2abf5SdYcEQ17HTekHpsMpGVy5p7ZD7Dhh/p+UY\nOPWqd2cdkQ9p1fdutvRks2QYJfj+aV/LKxgTZXDNAoPQnrb/jqrIbQoVPPBmD9ew\nx7aqYfRajmEBdgVuTqEhCjhN/jPnzKUYaEB1TYq22QKBgQDMZtVTfMZV7SDM4q4U\nBpmCN9cQc3meccD0IXl8ZK9wDG0/w87TKH1F9RMxp63d6yt0h+71ZhE1h6IcDYsc\nTtJhTzYjVj7FjM59lTxl+XbES1V3CNpCkHJatTevle7qwCCrNMZQfnuatLNK66jd\nhqvblJ+wBOMHY++UJp8temeS2wKBgQDIVfkUdnqpNOOniTnJ5Ls9W21gsRIFOgu2\nmeIlyTAj9IL6ELvaIJueTE1kfaERqSBkoAFV25l8Sf5s/BTwXlnnNo7O/3Qa+Q5N\neA2lYzyWeD/PJcB4w81x17/IPnJ+zd/lpQt9iDW6Fp7oY1HwF9tXv231WWDQbQhR\nPjKLYICdPQKBgHwf/m/il7bad060YS38DACN1GZDGZnkTl5ybYniwr7ybO2KBPEp\n51kySGOhBe57vznWyn/vaYfuQ71xZAbevtck+SVgXGIu7b5JgBIU+dCeRtowYAqI\nGUmIPra8AAhCgBQ3yi5bgMgj77URgsxz2a1QheCoNw3n3DdFdOhzKq59AoGBAIlT\nRZZdUN/EPXmOe2qFvEPm9CcfufaTP4xAF+FG9BTxewbniZ2QVJxCOZr08wAkKuxP\nMhskmSW1ow4aDlBmnMH9iA8k1PXYW5GHBfOk/tc2PqdEfZdKwP2UowYkqF97yEqm\nxCWcxRd2gh9SVcx6zgRsWHeieNbmppjqRcN8ty0RAoGAcZdNz6u78ibo/JcG1G5Z\nw7PD10q/bRp94STqxndQQHk3xct23o2JMaX2cdSYa0V/a5CXyxstWIR+B0dJORJJ\neA98OzS9NBXnR2TK49ketz5qnSAAe/SmwjYbuvCXgfgCnFWCfBQjwYCamZJpH6QG\nR7mjCfCnWzXvZULy22Efqkw=\n-----END PRIVATE KEY-----\n", "client_email": "tranxpert-mvp@appspot.gserviceaccount.com", "client_id": "105625998784101206937", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tranxpert-mvp%40appspot.gserviceaccount.com"}'


# from firebase_admin import tenant_mgt
# import firebase_admin
#
# json_acc_info = json.loads(firebase_default_service_account, strict=False)
# credentials = firebase_admin.credentials.Certificate(json_acc_info)
# firebase_app = firebase_admin.initialize_app(credentials)
#
# tenant = tenant_mgt.create_tenant(
#     display_name='devs',
#     enable_email_link_sign_in=True,
#     allow_password_sign_up=True)
#
# print('Created tenant:', tenant.tenant_id)


_DEFAULT_AUTH_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

# Replace the following values with your own values
project_id = "tranxpert-mvp"
api_key = "AIzaSyDE3qSVJKQc70O93yo5aGcmkyb1lfbG46g"
user_id = "marco.sandoval@tranxpert.com.mx"
new_tenant = "devs-bqt4c"


# Create the flow using the client secrets file from the Google API
# Console.
flow = Flow.from_client_config(
    json.loads(oauth_secrets),
    scopes=_DEFAULT_AUTH_SCOPES,
    redirect_uri='http://localhost:8502'
)

# Tell the user to go to the authorization URL.
auth_url, _ = flow.authorization_url(prompt='consent')

print('Please go to this URL: {}'.format(auth_url))

# The user will get an authorization code. This code is used to get the
# access token.
code = input('Enter the authorization code: ')
flow.fetch_token(code=code)
oauth_credentials = flow.credentials

print("Access token obtained from Google Auth flow consent")

import requests
import json


# # Construct the API endpoint URL
# url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?access_token={oauth_credentials.token}"
#
# # Set the request body
# payload = {
#     "email": [user_id]
# }
#
# # Convert the payload to a JSON string
# payload_json = json.dumps(payload)
#
# # Set the request headers
# headers = {
#     "Content-Type": "application/json"
# }
#
# # Send the API request
# response = requests.post(url, data=payload_json, headers=headers)
#
# # Check the response status code
# if response.status_code == 200:
#     user = response.json()["users"][0]
#     local_id = user["localId"]
#     print(f"Local ID for user {user}: {local_id}")
# else:
#     print(f"Error looking up user: {response.json()['error']['message']}")
#


#########################


# Construct the API endpoint URL
url = f"https://identitytoolkit.googleapis.com/v1/projects/{project_id}/accounts:update?access_token={oauth_credentials.token}"

# Set the request body
payload = {
    "localId": 'oqHdd10hnCf5StKgAMoMHT4EU0m1',
    "tenantId": 'development-auy9q'
}

# Convert the payload to a JSON string
payload_json = json.dumps(payload)

# Set the request headers
headers = {
    "Content-Type": "application/json"
}

# Send the API request
response = requests.post(url, data=payload_json, headers=headers)

# Check the response status code

print(response.content)

if response.status_code == 200:
    print("Tenant updated successfully.")
else:
    print(f"Error updating tenant: {response.json()['error']['message']}")
