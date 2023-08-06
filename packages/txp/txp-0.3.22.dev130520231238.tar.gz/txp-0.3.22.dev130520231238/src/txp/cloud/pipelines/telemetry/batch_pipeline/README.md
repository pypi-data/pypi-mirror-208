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

#### Testing

Using local job executor
```commandline
 python batch_pipeline.py --time_table tranxpert-mvp:telemetry_test.time --fft_table tranxpert-mvp:telemetry_test.fft --psd_table tranxpert-mvp:telemetry_test.psd --time_metrics_table tranxpert-mvp:telemetry_test.time_metrics --fft_metrics_table tranxpert-mvp:telemetry_test.fft_metrics --psd_metrics_table tranxpert-mvp:telemetry_test.psd_metrics --model_signals_topic_name txp-model-serving-signals-test
```

Using Dataflow job executor
```commandline
 python batch_pipeline.py --time_table tranxpert-mvp:telemetry_test.time --fft_table tranxpert-mvp:telemetry_test.fft --psd_table tranxpert-mvp:telemetry_test.psd --time_metrics_table tranxpert-mvp:telemetry_test.time_metrics --fft_metrics_table tranxpert-mvp:telemetry_test.fft_metrics --psd_metrics_table tranxpert-mvp:telemetry_test.psd_metrics --model_signals_topic_name txp-model-serving-signals-test --runner DataflowRunner --project tranxpert-mvp --region us-west4 --temp_location gs://telemetry-pipeline-bucket/tmp/ --staging_location gs://telemetry-pipeline-bucket/staging/ --job_name telemetry-batch-test --max_num_workers 1 --setup_file ./setup.py
```

#### Production
This pipeline SHOULD NOT be manually deployed, in production level GCP composer will deploy it.
