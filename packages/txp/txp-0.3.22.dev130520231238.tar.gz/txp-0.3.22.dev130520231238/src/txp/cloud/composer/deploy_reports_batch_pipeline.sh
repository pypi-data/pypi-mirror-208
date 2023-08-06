#!/bin/bash
#########################################################
#                     PARAMETERS                        #
#########################################################
composer_name="txp-composer"
dataset="reports"
reports_bucket="txp-reports"

composer_bucket=$1
composer_resources_bucket=$2

composer_dags_folder="$composer_bucket/dags/reports_generator/"
composer_resources_batch_pipeline_folder="$composer_resources_bucket/pipelines/reports/batch_pipeline/"

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $script_dir
cd ../
rm -rf dist
gsutil cp ./pipelines/reports/batch_pipeline/setup.py $composer_dags_folder
gsutil cp ./pipelines/reports/batch_pipeline/batch_pipeline.py $composer_resources_batch_pipeline_folder

location=$3


cd ./composer

echo Deploying reports batch pipeline
gcloud composer environments update $composer_name --update-pypi-packages-from-file requirements.txt --location $location
gcloud composer environments update $composer_name --location $location --update-env-variables=REPORTS_DATASET=$dataset,REPORTS_BUCKET=$reports_bucket,RESOURCES_BUCKET=$composer_resources_bucket,LOCATION=$location
gcloud composer environments storage dags import --environment $composer_name --location $location --source ./dag_reports_generator.py --project tranxpert-mvp