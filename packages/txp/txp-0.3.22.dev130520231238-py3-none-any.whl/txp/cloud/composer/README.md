# Cloud Composer.

This folder contains the Apache Airflow directed acyclic graph (DAG) files that runs in a Cloud Composer
environment.

This is our data production line in batch mode.

### Deploy Batch pipeline

#### Requirements
In order to fully deploy batch pipeline from the ground up we need to meet some requirements:

NOTE:
If you want to deploy the pipeline in production mode delete `_test` or `-test` suffix in the
objects created.

1. Firestore collections: we need to create some collections in firestore db. 
    * `pending_signal_chunks_test`
    * `signals_queue_test`

2. Bigquery dataset: 
   * create a new dataset for telemetry in Bigquery name it `telemetry_test`
   * run `src/txp_cloud/schemas/create_tables.py telemetry_test`
   * create a new dataset for events and states in Bigquery name it `ml_events_and_states_test`
   * run `src/txp_ml/schemas/create_tables.py ml_events_and_states_test`

3. GCS buckets:
    * create data lake bucket name it `tranxpert-mvp-telemetry-data-lake-test`
    * create composer resources bucket name it `composer-resources-test`
    * create folders path `composer-resources-test/pipelines/batch_pipeline`

4. PubSub topics:
   * create `txp-model-serving-signals-test` topic
   * create `txp-telemetry-batch-test`, this need to be also a register in IOT core

5. Create Composer environment:
   * create `txp-composer-test` environment location must match dataset location

#### Deploy

Run deploy_batch_pipeline.sh script to deploy batch pipeline.

```commandline
./deploy_telemetry_batch_pipeline.sh <ENVIRONMENT_BUCKET_URI> <COMPOSER_RESOURCES_URI> <TXP_CLOUD_UTILS_VERSION> <LOCATION>
```

Example production mode:
```commandline
./deploy_telemetry_batch_pipeline.sh gs://us-west4-txp-composer gs://composer-resources us-west4
```

For text mode edit parameters at deploy_telemetry_batch_pipeline