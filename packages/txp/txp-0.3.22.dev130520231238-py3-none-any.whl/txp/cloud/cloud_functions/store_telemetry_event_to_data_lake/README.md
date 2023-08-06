GCP Cloud Function: Stores telemetry data into data lake

This function will do: 

- Run every time a new telemetry event is published on txp-telemetry pub/sub topic by a Gateway in the project.
- Converts telemetry proto buffer event and creates many json files (one per each signal chunk).
- Stores json files to Google cloud storage data lake.
- Store signal path at pending signals' table on firestore db.

#### Deploy the function to GCP

- Generate the wheel f the `txp` project.
- Copy the wheel in the `./dist` folder
- Verify that the wheel name matches the specified wheel in requirements.txt`
- Deploy the function using `gcloud` with the command:

Production mode:

```commandline
gcloud functions deploy store_telemetry_event_to_data_lake --runtime python37 --trigger-topic txp-telemetry-batch
```

Test mode:
```commandline
gcloud functions deploy store_telemetry_event_to_data_lake_test --entry-point store_telemetry_event_to_data_lake --runtime python37 --trigger-topic txp-telemetry-batch-test --update-env-vars DATA_LAKE_BUCKET_NAME=telemetry-data-lake-test,PENDING_SIGNAL_CHUNKS_COLLECTION=pending_signal_chunks_test
```


[Reference](https://cloud.google.com/functions/docs/calling/pubsub#deploying_your_function).

#### Invoking the function

The function will be automatically triggered when a new telemetry package arrives in the specified telemetry topic.
