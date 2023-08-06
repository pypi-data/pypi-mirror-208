GCP Cloud Function: sends ml notification

This function will do: 

- Run every time a new ml state is reported.
- Deserialize notifications proto.
- Sends email to tenant notifying new email

#### Deploy the function to GCP

- Verify that project version matches the specified wheel in requirements.txt`
- Deploy the function using `gcloud` with the command:

Production mode:

```commandline
gcloud functions deploy ml_notifications --runtime python37 --trigger-topic txp-notifications --update-env-vars ACCOUNT_SID=<sid>,AUTH_TOKEN=<token>,WHATSAPP_NUMBER=<number>
```

Test mode:
```commandline
gcloud functions deploy ml_notifications_test --entry-point ml_notifications --runtime python37 --trigger-topic txp-notifications-local-test --update-env-vars ACCOUNT_SID=<sid>,AUTH_TOKEN=<token>,WHATSAPP_NUMBER=<number>
```


[Reference](https://cloud.google.com/functions/docs/calling/pubsub#deploying_your_function).

#### Invoking the function

The function will be automatically triggered when a new telemetry package arrives in the specified telemetry topic.