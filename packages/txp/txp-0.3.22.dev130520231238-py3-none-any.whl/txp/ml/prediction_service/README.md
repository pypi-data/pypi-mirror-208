# Model serving ray

## Parameters

* backup_collection_name : cache collection name used for ray service
* dataset : dataset where data is going to be looked for
* subscription_id : pubsub subscription id, where messages are going to be read from
* credentials_path: path to google credentials file

## Deploy model serving ray locally as test mode

Ray service is configured to run as test mode by default the simply run:

```commandline
python model_serving_ray.py
```

## Deploy model serving ray locally as production mode

We must provide correct parameters.

```commandline
python prediction_service.py --backup_collection_name ray_service_backup --dataset telemetry \
--subscription_id txp-model-serving-signals-sub \
--events_and_states_dataset ml_events_and_states \
--notifications_topic txp-notifications \
--reports_topic txp-reports \
--credentials_path ../../common/credentials/pub_sub_to_bigquery_credentials.json
```
