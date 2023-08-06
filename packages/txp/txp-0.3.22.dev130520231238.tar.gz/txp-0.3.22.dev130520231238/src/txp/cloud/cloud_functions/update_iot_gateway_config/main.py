"""
This module exports the GCP Cloud function to update the Cloud IoT Core Gateway devices
based on the Firestore project configuration, specifically the most recent one.

It should be triggered after the creation of a Gateway Document in Firestore.
"""
from google.cloud import firestore
from txp.common.configuration import GatewayConfig, JobConfig
from txp.common.edge import MachineMetadata, EdgeDescriptor
from txp.common.models import *
from google.cloud import iot_v1
import json
import logging

from txp.common.utils.json_complex_encoder import ComplexEncoder


def _update_gateway_configuration(
    iot: iot_v1.DeviceManagerClient,
    configuration_id: int,
    job: JobConfig,
    gateway_config: GatewayConfig,
    machines: List[MachineMetadata],
    edges: List[EdgeDescriptor],
) -> None:
    """Updates the configuration of the Gateway in the IoT Core service."""
    device_path = iot.device_path(
        gateway_config.project_id,
        gateway_config.cloud_region,
        gateway_config.registry_id,
        gateway_config.gateway_id,
    )

    data = json.dumps(
        {
            "configuration_id": configuration_id,
            "job": job,
            "gateway": gateway_config,
            "machines": machines,
            "edges": edges,
        },
        cls=ComplexEncoder,
        indent=4,
    ).encode()

    iot.modify_cloud_to_device_config(
        request={
            "name": device_path,
            "binary_data": data,
            "version_to_update": 0
            # https://googleapis.dev/python/cloudiot/latest/iot_v1/types.html#google.cloud.iot_v1.types.ModifyCloudToDeviceConfigRequest.version_to_update
        }
    )


def _get_edges_descriptor(devices: List[Device], edges: List[Edge]):
    device_dict: Dict[str, Dict] = {}
    for d in devices:
        device_dict[d.kind] = d.get_dict()

    edges_descriptors: List[EdgeDescriptor] = []
    for e in edges:
        e_dict = e.get_dict()
        descriptor = EdgeDescriptor(
            e.logical_id,
            e.device_kind,
            e.type,
            {
                **device_dict[e.device_kind]["parameters"],
                **e_dict.get("parameters", {}),
            },
            {
                **device_dict[e.device_kind]["perceptions"],
                **e_dict.get("perceptions", {}),
            },
        )
        edges_descriptors.append(descriptor)
    return edges_descriptors


def _get_query(
    model_ref, tenant_id
):
    return FirestoreModelsQuery(
        model_ref,
        tenant_id,
        [],
        model_ref.get_db_query_fields(
            [models_pb2.ALWAYS_REQUIRED, models_pb2.IOT_DEVICES_REQUIRED]
        )
    )


def _query_required_entities(
    tenant_id
):
    # Query for Gateway Entities
    db_models = FirestoreModelsClient(None)
    assets = _get_query(Asset, tenant_id)
    devices = _get_query(Device, tenant_id)
    jobs = _get_query(SamplingJob, tenant_id)
    edges = _get_query(Edge, tenant_id)
    db_models.add_query(assets)
    db_models.add_query(devices)
    db_models.add_query(jobs)
    db_models.add_query(edges)
    r = db_models.get_query_results()
    return r


# ======================== Main Function Body to export ============================================
def update_iot_gateways_conf(data, context):
    """The cloud function body defined in this module, to be deployed as a GCP cloud function.

    Documentation reference for the received arguments as result of a Firestore trigger:
        https://cloud.google.com/functions/docs/calling/cloud-firestore#event_structure
    """
    db = firestore.Client()
    gateway_document_name = data["value"][
        "name"
    ]  # This keys are guaranteed by Firestore trigger payload
    gateway_document: firestore.DocumentSnapshot = db.document(
        gateway_document_name
    ).get()

    # Obtain tenant-id
    configuration_ref = gateway_document.get("configuration_ref")
    tenant_id = configuration_ref.get().get("tenant_ref").get().get("tenant_id")

    # Do queries
    r = _query_required_entities(tenant_id)

    machines: List[Asset] = r[0]
    jobs: List[SamplingJob] = r[2]
    devices = r[1]
    edges = r[3]

    # Get Machines Ids
    machines_ids: List[str] = list(
        map(lambda machine_doc: machine_doc.asset_id, machines)
    )

    # Filter only machines that belongs to the Gateway
    machines_ids = list(
        filter(lambda _id: _id in gateway_document.to_dict()["assets"], machines_ids)
    )

    # Creates legacy Gateway Config
    gateway_config: GatewayConfig = GatewayConfig.build_from_dict(
        {**gateway_document.to_dict(), **{"machines_ids": machines_ids}}
    )

    # Creates Legacy JobConfig instance
    jobs = list(filter(lambda j: j.job_id == gateway_document.get("has_job"), jobs))
    job_config: JobConfig = JobConfig.build_from_dict(
        jobs[0].get_dict(include_defautls=True)
    )

    # Creates Legacy Machines Metadata entities
    machines_metadata: List[MachineMetadata] = list(
        map(
            lambda asset: MachineMetadata.build_from_dict(
                {
                    "machine_id": asset.asset_id,
                    "model": "",
                    "manufacturer": "",
                    "edges_ids": asset.associated_with_edges,
                    "state_manager": "",
                    "tasks": {},
                }
            ),
            machines,
        )
    )

    machines_metadata = list(
        filter(lambda m: m.machine_id in gateway_config.machines_ids, machines_metadata)
    )

    # Filters the edges that we care about
    edges_ids = []
    for machine in machines_metadata:
        edges_ids.extend(machine.edges_ids)

    edges = list(filter(lambda e: e.logical_id in edges_ids, edges))

    descriptors = _get_edges_descriptor(devices, edges)

    iot = iot_v1.DeviceManagerClient()
    _update_gateway_configuration(
        iot,
        configuration_ref.get().get("configuration_id"),
        job_config,
        gateway_config,
        machines_metadata,
        descriptors,
    )

    print(f"Successfully updated the Gateway: {gateway_config.gateway_id} in IoT")


# ======================== Main to debug locally ============================================
if __name__ == "__main__":
    # debug using the GAO standalone-arm gateway
    update_iot_gateways_conf({"value": {"name": "gateways/DOy5Lm635nLcnznpAIS1"}}, {})
