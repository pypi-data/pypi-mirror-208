"""
This module exports a function that can be deployed as a GCP Cloud function
capable of updating the TXP Firestore configuration based on the manual
configuration editable collection.

The Manual Configuration Editable collection is a special collection in our
Firestore database, that can be used to edit configurations using the Firestore
web console.

This is provided as a way to edit configuration while we develop a web client
to communicate with Firestore.
"""

# =========================== Imports ===============================
from txp.common.models import *
from txp.common.config import settings
import google.cloud.firestore as firestore
import txp.common.configuration.config_version as txp_config_version
from txp.common.utils.firestore_utils import (
    pull_current_configuration_from_firestore
)
from google.protobuf.json_format import MessageToDict
from typing import List, Dict, Union
import txp.common.utils.firestore_utils
import pytz
import datetime
import logging

log = logging.getLogger(__name__)

# =========================== Constant Data ===============================
manual_configuration_collection = (
    settings.firestore.manual_configuration_edit_collection
)

configurations_collection_name = settings.firestore.configurations_collection
tenants_collection = txp.common.utils.firestore_utils.tenants_collection
machines_group_collection_name = settings.firestore.machines_group_collection


# =========================== Helper Functions ===============================
def pull_docs_from_manual_form_collection(
        db: firestore.Client, configuration_document: str, subcollection: str, as_dict: bool = True
) -> Union[List[Dict], List[firestore.DocumentSnapshot]]:
    """Returns the Dict instances from the documents found in the
    collection for the manual configuration form collection"""
    db
    documents_coll = (
        db.collection(manual_configuration_collection)
            .document(configuration_document)
            .collection(subcollection)
            .get()
    )

    documents_coll = list(filter(
        lambda doc: "template" not in doc.id, documents_coll
    ))

    if as_dict:
        documents_coll = list(map(
            lambda doc: doc.to_dict(), documents_coll
        ))

    return documents_coll


def _create_new_configuration(
        db: firestore.Client,
        tenant_reference: firestore.DocumentReference
) -> firestore.DocumentReference:
    """Creates a new entity (document) in the configurations root level collection.

    The configuration time is aware time for UTC zone.
    The configuration entity has a timestamp based on the Firestore server,
        in order to support queries by timestamp.

    Returns:
        The DocumentReference to the new configuration entity.
    """
    previous_configuration = pull_current_configuration_from_firestore(db, tenant_reference.get().get('tenant_id'))

    if (previous_configuration and
            previous_configuration.exists and
            'configuration_id' in previous_configuration.to_dict()):
        new_configuration_id = txp_config_version.get_next_normal_version(
            previous_configuration.to_dict()['configuration_id']
        )
    else:
        new_configuration_id = 1

    config_timestamp = datetime.datetime.now(pytz.timezone(settings.gateway.timezone)).replace(microsecond=0)
    ref = db.collection(configurations_collection_name).add(
        {
            "configuration_id": str(new_configuration_id),  # string to allow possible id generation in the future
            # TODO: Remove `since` key if nobody is using it. This is local time eventually turned into UTC by Firestore
            "since": config_timestamp,
            "server_timestamp": firestore.SERVER_TIMESTAMP,  # This will be UTC
            "tenant_ref": tenant_reference
        }
    )
    return ref[1]


def _add_perceptions_to_edges(edges: List[Edge], devices: List[Device]):
    # device perception map
    dpm = {}
    for d in devices:
        dpm[d['kind']] = d['perceptions']

    for e in edges:
        e['perceptions'] = dpm[e['device_kind']]

    return


def _create_documents_in_collection(
    db: firestore.Client,
    entities: List,
    class_ref: TxpRelationalEntity,
    configuration_ref: firestore.DocumentReference,
):
    for p in entities:
        d = MessageToDict(p, preserving_proto_field_name=True)
        d["configuration_ref"] = configuration_ref
        result = db.collection(class_ref.firestore_collection_name()).add(d)
    log.info(f"Entities successfully added in remote Firestore DB")

# ======================== Main Function Body to export ============================================
def update_manual_configuration(request):
    """The cloud function body defined in this module, to be deployed
        as a GCP cloud function.

        This method will generate a manual configuration snapshot given the
        tenant-id and the manual configuration collection stored in firestore.

        Args:
            request (flask.Request): The request object.
            <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>

        Returns:
            200 OK status code if everything was successful.

    """
    print(request)
    request_json = request.get_json(silent=True)
    print(request_json)
    if request_json and 'tenant_id' in request_json:
        tenant_id = request_json['tenant_id']
        configuration_document = request_json['configuration_document']
        log.info(f"Tenant ID received: {tenant_id}")
        log.info(f"Configuration Document in {manual_configuration_collection}"
                 f" collection: {configuration_document}")
    else:
        raise ValueError("JSON is invalid, or missing a 'name' property")

    db = firestore.Client()
    log.info(f"Trying to find Tenant document for {tenant_id}...")

    # Pull the tenant Document
    tenant = db.collection(tenants_collection).where(
        'tenant_id', '==', tenant_id
    ).get()

    if not tenant:
        log.error(f"Tenant document was not found for {tenant_id}")
        return 404

    if len(tenant) > 1:
        log.warning(f"Multiple Tenants in the database with id: {tenant_id}.")

    tenant_ref = tenant[0].reference

    log.info(
        "Connection to Firestore established. Proceed to pulling entities from manual"
        f"configuration form {configuration_document}"
    )

    assets_groups: List[Dict] = pull_docs_from_manual_form_collection(
        db, configuration_document, AssetsGroup.firestore_collection_name()
    )

    if not assets_groups:
        log.error("No machines_groups documents found. Execution finished")
        return "Error: No machines_groups found\n", 500

    assets: List[Dict] = pull_docs_from_manual_form_collection(
        db, configuration_document, Asset.firestore_collection_name())

    if not assets:
        log.error("No machines documents found. Execution finished")
        return "Error: No machines found in database form\n", 500

    gateways: List[Dict] = pull_docs_from_manual_form_collection(
            db, configuration_document, Gateway.firestore_collection_name())

    if not gateways:
        log.error("No gateways documents found. Execution finished")
        return "Error: No gateways found in database form\n", 500

    devices: List[Dict] = pull_docs_from_manual_form_collection(
        db, configuration_document, Device.firestore_collection_name())

    if not devices:
        log.error("No devices documents found. Execution finished")
        return "Error: No devices found in database form\n", 500

    edges: List[Dict] = pull_docs_from_manual_form_collection(
        db, configuration_document, Edge.firestore_collection_name())

    if not edges:
        log.error("No edges documents found. Execution finished")
        return "Error: No edges found in database form\n", 500

    jobs = pull_docs_from_manual_form_collection(
        db, configuration_document, SamplingJob.firestore_collection_name()
    )

    if not jobs:
        log.error("No jobs document found. Execution finished")
        return "Error: No job entity found in database form\n", 500

    log.info(
        "All the required entities were obtained from the manual configuration form document"
    )

    _add_perceptions_to_edges(edges, devices)

    assets_groups = list(map(
        lambda ag: AssetsGroup.get_proto_from_dict(ag),
        assets_groups
    ))
    log.info("AssetsGroups entities were correct evaluated.")

    assets = list(map(
        lambda ad: Asset.get_proto_from_dict(ad),
        assets
    ))
    log.info("Assets entities were correct evaluated.")

    devices = list(map(
        lambda d: Device.get_proto_from_dict(d),
        devices
    ))
    log.info("Devices entities were correct evaluated.")

    edges = list(map(
        lambda e: Edge.get_proto_from_dict(e),
        edges
    ))
    log.info("Edges entities were correct evaluated.")

    gateways = list(map(
        lambda g: Gateway.get_proto_from_dict(g),
        gateways
    ))
    log.info("Gateways entities were correct evaluated.")

    jobs = list(map(
        lambda j: SamplingJob.get_proto_from_dict(j),
        jobs
    ))
    log.info("Jobs entities were correct evaluated.")

    created_configuration_ref = _create_new_configuration(db, tenant_ref)

    _create_documents_in_collection(db, assets_groups, AssetsGroup, created_configuration_ref)

    _create_documents_in_collection(db, assets, Asset, created_configuration_ref)

    _create_documents_in_collection(db, devices, Device, created_configuration_ref)

    _create_documents_in_collection(db, edges, Edge, created_configuration_ref)

    _create_documents_in_collection(db, jobs, SamplingJob, created_configuration_ref)

    _create_documents_in_collection(db, gateways, Gateway, created_configuration_ref)

    log.info("All the new entities were created for the new configuration snapshot")

    return "OK\n", 200

# ======================== Main program to debug locally ============================================
if __name__ == "__main__":
    from unittest.mock import Mock

    tenant_id = 'labshowroom-001'
    configuration_document = 'laboratorio_showroom_manual_script'
    data = {'tenant_id': tenant_id, 'configuration_document': configuration_document}
    req = Mock(get_json=Mock(return_value=data), args=data)
    update_manual_configuration(req)
