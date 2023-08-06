GCP Cloud Function: Process IoT State event to Firestore model

This function will do: 

- Run every time a new state event published by a Gateway in the project is received in IoT/PubSub. 
- Process the state event received and prepare the Firestore update for the database entities of the snapshot.
- Update the edges/gateway state in Firestore

#### Deploy the function to GCP

- Generate the wheel f the `txp` project.
- Copy the wheel in the `./dist` folder
- Verify that the wheel name matches the specified wheel in requirements.txt`
- Deploy the function using `gcloud` with the command:

```commandline
gcloud functions deploy process_state_event_to_firestore --trigger-topic projects/tranxpert-mvp/topics/txp-states 
```

[Reference](https://cloud.google.com/functions/docs/calling/pubsub#deploying_your_function).

#### Invoking the function

The function will be automatically triggered when a new state arrives in the specified states topic.
