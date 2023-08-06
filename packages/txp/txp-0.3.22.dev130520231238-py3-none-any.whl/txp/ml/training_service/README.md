# Training Service

This service is used for create, train and publish models.

## Endpoints


### Commit new dataset, POST /training/commit

example:

```json
{
    "bigquery_dataset": "telemetry_test",
    "dataset_name": "Vibrations",
    "dataset_versions": ["1", "2"],
    "start": "2022-06-21 10:00:00",
    "end": "2022-06-21 12:00:00",
    "tenant_id": "labshowroom-001",
    "machine_id": "Motor_lab",
    "task_id": "Motor_lab_1"
}
```

### Train new model, POST /training/train

example:

```json
{
    "dataset_name": "Vibrations",
    "dataset_versions": ["1", "2"],
    "tenant_id": "labshowroom-001",
    "machine_id": "Motor_lab",
    "task_id": "Motor_lab_1"
}
```

### Publish new model, POST /training/publish

example:

```json
{
    "dataset_name": "Vibrations",
    "dataset_versions": ["1", "2"],
    "tenant_id": "labshowroom-001",
    "machine_id": "Motor_lab",
    "task_id": "Motor_lab_1"
}
```

### Ping service, GET /training/

example response:

200 OK
```json
{
    "message": "Training service is up and running"
}
```
