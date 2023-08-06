## Tranxpert Dashboard

This folder contains the extra `dashboard` package
from `txp`. 

It contains all the code related to the Dash Web application
for monitoring. 

-------

### Docker Artifact Registry

The file `app.Dockerfile` contains the build instructions to build a Docker
 image of the application that can be stored in some Docker repository service.

We use GCP Artifacts Registry to store the Docker image. 
That image can be used in Cloud Run, to be deployed as a managed service. 

Instructions for generating the docker image are detailed in below steps: 

#### Build the Docker Image

- Open a terminal inside the `dashboard` folder.
- Ensure that the following files exists: 
    - `auth.tom` Secrets file to authenticate in Identity Platform
    - `pub_sub_to_bigquery_credentials.json` Secret service accoun  to authenticate in cloud services.  

- Build the Docker image using the command: 

```terminal
docker build -f app.Dockerfile us-central1-docker.pkg.dev/tranxpert-mvp/txp-dashboard-docker-repo/txp-dashboard:[TAG]
```

#### Push the Docker Image to Artifacts Registry

Configure Docker, and Artifacts Registry for your project. 
Steps are summarized [here](https://medium.com/kunder/deploying-dash-to-cloud-run-5-minutes-c026eeea46d4).
