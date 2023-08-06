# GCP Cloud function: Update IoT devce configuration from firestore

This function will do:


- Run every time a new Gateway document is created in the gateways collection
in Firestore, as part of a new configuration update. When a new snapshot is generated, 
  the gateways will be generated last, and when a gateway document is created, the function
  will execute. 

- Connect to Firestore to pull down the most recent configuration entities for the 
  created gateway.

- Process the received documents to update the Gateway configuration in the
IoT Core service. 
  

### Deploy the Function to GCP

- Generate the wheel of the `txp` project.


- Copy the wheel in the `./dist` folder.


- Verify that the wheel name matches the specified wheel in `requirements.txt`


- Deploy the function using `gcloud` with a terminal in this folder:

```commandline
gcloud functions deploy update_iot_gateways_conf --runtime "python37" 
--trigger-event "providers/cloud.firestore/eventTypes/document.create"
--trigger-resource "projects/{project_id}/databases/(default)/documents/gateways/{gateway}"
```

The `gcloud` should deploy the cloud function. 


### Invoking the function

The function will be automatically triggered when a new document
is created in the configurations collection. 
