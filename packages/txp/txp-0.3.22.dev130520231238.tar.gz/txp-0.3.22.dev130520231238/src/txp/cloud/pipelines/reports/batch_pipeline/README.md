# Batch Pipeline (Apache).

## Steps for consuming data available in data lake and storing it to BigQuery

### Requirements
1. Uses the cloud function store_telemetry_event_to_data_lake to process the notifications sends by the composer
whichs verifies the completeness of the signals available in the dat lake.
2. Create a BigQuery dataset and 2 tables for storing fft and raw samples.
Schemas can be found in ```src/txp_cloud/pipelines/pub_sub_to_bigquery/schemas```.
3. Create a Cloud Storage bucket.
4. Create a service account with following roles:

    *BigQuery Data Editor*

    *Storage Admin*

    *Service Account User*

    *Dataflow Admin*

### Running the pipeline:

Using local job executor
```commandline
python batch_pipeline.py --reports_dataset tranxpert-mvp:reports --tenant_id labshowroom-001 \
--start_datetime '2022-10-03 11:00:00.0+0000' --end_datetime '2022-10-04 11:00:00.0+0000' \
--reports_bucket_name txp-reports --notifications_user <USER> \
--notifications_password <PASS> \
--notifications_url 'https://notifications-api-dot-tranxpert-mvp.uw.r.appspot.com/send-report'
```

Using Dataflow job executor
```commandline
python batch_pipeline.py \
--reports_dataset tranxpert-mvp:reports --tenant_id labshowroom-001 \
--start_datetime '2022-10-03 11:00:00.0+0000' --end_datetime '2022-10-04 11:00:00.0+0000' \
--reports_bucket_name txp-reports \
--reports_bucket_name txp-reports --notifications_user <USER> \
--notifications_password <PASS> \
--notifications_url 'https://notifications-api-dot-tranxpert-mvp.uw.r.appspot.com/send-report' \
--runner DataflowRunner --project tranxpert-mvp --region us-west4 \
--temp_location gs://txp-reports-bucket --job_name reports-batch-test \
--max_num_workers 1 \
--setup_file ./setup.py
```

