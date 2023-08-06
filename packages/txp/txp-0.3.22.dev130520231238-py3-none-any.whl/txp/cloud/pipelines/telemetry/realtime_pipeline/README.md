# Pub/Sub to BigQuery, Apache Beam pipeline.

## Steps for consuming data in Pub/Sub topic and storing it to BigQuery

### Requirements
1. Create a PubSub topic and a pull subscription.
2. Execute create tables script at ```src/txp/cloud/pipelines/telemetry/schemas/create_tables.py``` .
3. Create a Cloud Storage bucket.
4. Create a service account with following roles:

    *Pub/Sub Subscriber* 

    *BigQuery Data Editor*

    *Storage Admin*

    *Service Account User*

    *Dataflow Admin*

    *Pub/Sub Publisher*

### Running the pipeline:

#### Testing:

We could run the realtime pipeline with local executor as follows:

```commandline
python realtime_pipeline.py --streaming --input_subscription projects/tranxpert-mvp/subscriptions/txp-telemetry-realtime-test-sub --time_table tranxpert-mvp:telemetry_test.time --fft_table tranxpert-mvp:telemetry_test.fft --psd_table tranxpert-mvp:telemetry_test.psd --time_metrics_table tranxpert-mvp:telemetry_test.time_metrics --fft_metrics_table tranxpert-mvp:telemetry_test.fft_metrics --psd_metrics_table tranxpert-mvp:telemetry_test.psd_metrics --model_signals_topic_name txp-model-serving-signals-test
```

If we want to run the realtime pipeline with Dataflow executor as follows:


```commandline
python realtime_pipeline.py --streaming --input_subscription projects/tranxpert-mvp/subscriptions/txp-telemetry-realtime-test-sub --time_table tranxpert-mvp:telemetry_test.time --fft_table tranxpert-mvp:telemetry_test.fft --psd_table tranxpert-mvp:telemetry_test.psd --time_metrics_table tranxpert-mvp:telemetry_test.time_metrics --fft_metrics_table tranxpert-mvp:telemetry_test.fft_metrics --psd_metrics_table tranxpert-mvp:telemetry_test.psd_metrics --model_signals_topic_name txp-model-serving-signals-test --runner DataflowRunner --project tranxpert-mvp --region us-west4 --temp_location gs://telemetry-pipeline-bucket --job_name telemetry-test --max_num_workers 1 --setup_file ./setup.py
```

#### Production:

```commandline
python realtime_pipeline.py --streaming --input_subscription projects/tranxpert-mvp/subscriptions/txp-telemetry-realtime-sub --time_table tranxpert-mvp:telemetry.time --fft_table tranxpert-mvp:telemetry.fft --psd_table tranxpert-mvp:telemetry.psd --time_metrics_table tranxpert-mvp:telemetry.time_metrics --fft_metrics_table tranxpert-mvp:telemetry.fft_metrics --psd_metrics_table tranxpert-mvp:telemetry.psd_metrics --model_signals_topic_name txp-model-serving-signals --runner DataflowRunner --project tranxpert-mvp --region us-west4 --temp_location gs://telemetry-pipeline-bucket --job_name telemetry --max_num_workers 1 --setup_file ./setup.py 
```
