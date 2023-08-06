# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8-slim-buster

# Python Unbuffered to read building logs
ENV PYTHONUNBUFFERED True

ENV APP_HOME ~
WORKDIR $APP_HOME

# Install Python dependencies and Gunicorn
RUN pip install --no-cache-dir txp[dashboard] && pip install --no-cache-dir gunicorn
RUN groupadd -r app && useradd -r -g app app

COPY auth.toml /usr/local/lib/python3.8/site-packages/txp/dashboard
COPY pub_sub_to_bigquery_credentials.json /usr/local/lib/python3.8/site-packages/txp/common/credentials/
ADD . .

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available in Cloud Run.
CMD exec gunicorn --bind :$PORT --log-level info --workers 1 --threads 8 --timeout 0 app:server
