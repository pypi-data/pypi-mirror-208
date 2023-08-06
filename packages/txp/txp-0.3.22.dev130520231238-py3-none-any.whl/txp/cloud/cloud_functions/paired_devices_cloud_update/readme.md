GCP Cloud Function: Update paired devices information in Firestore model

This function will do: 
   
- Run every time the Gateway publish an event after a production/devices pairing process, in the topic: `txp-devices-pairing`
- Process the received event published by the Gateway. 
- Update the appropriate edges in the model project stored in Firestore, for the current configuration version.
- Update the Gateway IoT Configuration with the paired edges new information. 


#### Deploy the function to GCP

- Generate the wheel for the `txp` project.
- Copy the wheel in the `./dist` folder
- Verify that the wheel name matches the specified wheel in requirements.txt`
- Deploy the function using `gcloud` with the command: 

```commandline
gcloud functions deploy update_paired_devices --trigger-topic txp-devices-pairing
```

[Reference](https://cloud.google.com/functions/docs/calling/pubsub#deploying_your_function).

#### Invoking the function

The function will be automatically triggered when a new state arrives in the specified states topic.
