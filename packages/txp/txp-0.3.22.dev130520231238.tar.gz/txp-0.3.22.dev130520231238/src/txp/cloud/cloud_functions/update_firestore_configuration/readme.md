# GCP Cloud Function: Update Firestore Manual Configuration

This function will do:


- Connect to `Firestore` to pull the `manual_configuration_edit` collection. 


- Process the received documents to create a new configuration "snapshot". The snapshot
is a new set of entities related to a new timestamped configuration. 

### Deploy the Function to GCP


- Generate the wheel of the `txp` project.
  

- Copy the wheel in the `./dist` folder.


- Verify that the wheel name matches the specified wheel in `requirements.txt`


- Deploy the function using `gcloud` with a terminal in this folder:

```commandline
gcloud functions deploy update_firestore_from_firestore --runtime "python37" --trigger-http
```


The `gcloud` should deploy the cloud function. 


### Invoking the function

You can run the function by using the HTTP endpoint provided by GCP.
Here's an example using `curl`:

```commandline
curl https://<CLOUD_REGION>-<PROJECT_ID>.cloudfunctions.net/update_firestore_from_firestore 
    -H "Authorization: bearer $(gcloud auth print-identity-token)"
    -H "Content-Type: application/json"
    -d { "tenant_id": "<YOUR TENANT VALUE>" } 
```
