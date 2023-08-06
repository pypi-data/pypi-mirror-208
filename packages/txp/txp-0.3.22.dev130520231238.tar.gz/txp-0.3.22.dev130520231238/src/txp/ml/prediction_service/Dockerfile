# Creates a ray docker image with Java on it.
# And also contains the fat .jar of the application.

# To build this dockerfile, please take a look to this command:
#   docker build --build-arg wheel_filename="txp-0.1.112-py3-none-any.whl" -f Dockerfile -t txp-ray-env:0.02 .

# To run this docker container, please take a look to this command:
# docker run --shm-size=1.17gb -d  txp-ray-env:0.02

FROM rayproject/ray:1.12.0

# wheel_file: The local machine file path to the TXP wheel
ARG wheel_path="."
ARG wheel_filename

WORKDIR /home/ray

# Install dependencies for ML Tasks in the TXP model serving service
RUN pip install --upgrade pip && \
    pip install opencv-python-headless && \
    pip install scikit-learn && \
    pip install scikit-image && \
    pip install xgboost && \
    pip install google-cloud-pubsub && \
    pip install segments-ai

# Copy the txp .wheel package dist. Taking it from home folder in running machine and
# install the txp .wheel package dist in the container image.
COPY $wheel_path/$wheel_filename .
RUN  pip install $wheel_filename --use-deprecated=legacy-resolver

RUN mkdir /home/ray/credentials
COPY credentials/pub_sub_to_bigquery_credentials.json credentials/pub_sub_to_bigquery_credentials.json

# Calls python unbuffered
ENTRYPOINT python -u /home/ray/anaconda3/lib/python3.7/site-packages/txp_ml/model_serving_ray.py --dataset='telemetry' --subscription_id='txp-model-serving-signals-sub'
