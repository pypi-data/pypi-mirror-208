#!/bin/bash
#########################################################
#                     PARAMETERS                        #
#########################################################
composer_name="txp-composer"
pending_signal_chunks_collection_name="pending_signal_chunks"
signals_queue_collection="signals_queue"
dataset="telemetry"
model_signals_topic_name="txp-model-serving-signals"
data_lake_bucket_name="tranxpert-mvp-telemetry-data-lake"
topic_id="txp-telemetry-batch"
cloud_function_name="store_telemetry_event_to_data_lake"

composer_bucket=$1
composer_resources_bucket=$2

composer_dags_folder="$composer_bucket/dags/signals_publisher/"
composer_resources_batch_pipeline_folder="$composer_resources_bucket/pipelines/telemetry/batch_pipeline/"

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $script_dir
cd ../
rm -rf dist
gsutil cp ./pipelines/telemetry/batch_pipeline/setup.py $composer_dags_folder
gsutil cp ./pipelines/telemetry/batch_pipeline/batch_pipeline.py $composer_resources_batch_pipeline_folder

location=$3


cd ./composer

echo Deploying telemetry batch pipeline
gcloud composer environments update $composer_name --update-pypi-packages-from-file requirements.txt \
  --location $location
gcloud composer environments update $composer_name --location $location \
--update-env-variables=PENDING_SIGNALS_CHUNKS_COLLECTION=$pending_signal_chunks_collection_name,SIGNALS_QUEUE_COLLECTION=$signals_queue_collection,TELEMETRY_DATASET=$dataset,MODEL_SIGNALS_TOPIC_NAME=$model_signals_topic_name,DATA_LAKE=$data_lake_bucket_name,RESOURCES_BUCKET=$composer_resources_bucket,LOCATION=$location
gcloud composer environments storage dags import --environment $composer_name --location $location \
  --source ./dag_signals_publisher.py --project tranxpert-mvp

cd ../cloud_functions/store_telemetry_event_to_data_lake

gcloud functions deploy $cloud_function_name --entry-point store_telemetry_event_to_data_lake \
    --runtime python37 --trigger-topic $topic_id \
    --update-env-vars DATA_LAKE_BUCKET_NAME=$data_lake_bucket_name,PENDING_SIGNAL_CHUNKS_COLLECTION=$pending_signal_chunks_collection_name