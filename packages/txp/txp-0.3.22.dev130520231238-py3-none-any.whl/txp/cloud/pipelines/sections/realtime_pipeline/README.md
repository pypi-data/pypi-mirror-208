# Pub/Sub to BigQuery, Apache Beam pipeline.

## Steps for consuming data in Pub/Sub topic and storing it to BigQuery

### Requirements
1. Create a PubSub topic and a pull subscription.
2. Execute create tables script at ```src/txp/cloud/pipelines/sections/schemas/create_tables.py``` .
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
python realtime_pipeline.py \
--streaming \
--input_subscription projects/tranxpert-mvp/subscriptions/txp-reports-sub \
--time_table tranxpert-mvp:telemetry.time \
--fft_table tranxpert-mvp:telemetry.fft \
--psd_table tranxpert-mvp:telemetry.psd \
--time_metrics_table tranxpert-mvp:telemetry.time_metrics \
--fft_metrics_table tranxpert-mvp:telemetry.fft_metrics \
--psd_metrics_table tranxpert-mvp:telemetry.psd_metrics \
--states_table tranxpert-mvp:ml_events_and_states.states \
--events_table tranxpert-mvp:ml_events_and_states.events \
--sections_table tranxpert-mvp:reports.sections 
```

#### Production:

```commandline
python realtime_pipeline.py \
--streaming \
--input_subscription projects/tranxpert-mvp/subscriptions/txp-reports-sub \
--time_table tranxpert-mvp:telemetry.time \
--fft_table tranxpert-mvp:telemetry.fft \
--psd_table tranxpert-mvp:telemetry.psd \
--time_metrics_table tranxpert-mvp:telemetry.time_metrics \
--fft_metrics_table tranxpert-mvp:telemetry.fft_metrics \
--psd_metrics_table tranxpert-mvp:telemetry.psd_metrics \
--states_table tranxpert-mvp:ml_events_and_states.states \
--events_table tranxpert-mvp:ml_events_and_states.events \
--sections_table tranxpert-mvp:reports.sections \
--runner DataflowRunner \
--project tranxpert-mvp \
--region us-west4 \
--temp_location gs://telemetry-pipeline-bucket \
--job_name sections \
--max_num_workers 1 \
--setup_file ./setup.py 
```
