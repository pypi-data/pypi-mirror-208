# Webhook for DialogFlow Fulfillment

This is a webhook for DialogFlow fulfillment requests. It is built on FastAPI and runs as a Google App Engine application.

## Endpoint

- https://tranxpert-mvp.uw.r.appspot.com/dialogflow-webhook

## Set environtment Variables

The following environment variables must be set (.env file for development and app.yaml for deployment):

- TWILIO_AUTH_TOKEN
- TWILIO_ACCOUNT_SID
- API_USERNAME
- API_PASSWORD
- TEST_WHATSAPP_NUMBER (example: *whatsapp:+535353535353*)

## Deploy

Login with gcloud:

```commandline
gcloud auth list
gcloud auth login
gcloud auth activate-service-account tranxpert-mvp@appspot.gserviceaccount.com --key-file=tranxpert-mvp-7d12c8755ba5.json
```

Create the app (if it does not exist):

```commandline
gcloud app create
gcloud components install app-engine-python
```

Run the configuration described in app.yaml:

```commandline
gcloud app deploy app.yaml
```

## Check the service running on App Engine

```commandline
gcloud app services list
gcloud app logs tail -s default
```

## Credentials for BigQuery and Firestore

To be able to make queries using BigQuery and Firestore it is necessary to have a credentials file in the path: `./credentials/pub_sub_to_bigquery_credentials.json`. You can copy this file from `src/txp/cloud/notifications/reactive/credentials/pub_sub_to_bigquery_credentials.json`.
