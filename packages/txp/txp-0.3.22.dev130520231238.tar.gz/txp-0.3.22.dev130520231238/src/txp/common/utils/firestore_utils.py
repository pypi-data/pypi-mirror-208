import datetime
import enum
import json
import traceback
from typing import Optional, List, Dict
import time

import pytz
from google.cloud import firestore as firestore
from txp.common.config import settings
from txp.common.configuration import GatewayConfig, JobConfig, config_version as txp_config_version
from txp.common.edge import MachineMetadata, EdgeDescriptor
from txp.common.ml.tasks import AssetTask
from txp.common.utils.json_complex_encoder import ComplexEncoder
from concurrent.futures import ThreadPoolExecutor, wait
import logging

log = logging.getLogger(__name__)

edges_collection_name = settings.firestore.edges_collection
machines_collection_name = 'assets'
tenants_collection = settings.firestore.tenants_collection
tenants_collection_name = tenants_collection
configuration_id_field = "configuration_id"
manual_configuration_collection = (
    settings.firestore.manual_configuration_edit_collection
)
config_form_document = settings.firestore.config_form_document
machines_group_collection_name = "assets_groups"
gateways_collection_name = settings.firestore.gateways_collection
devices_collection_name = settings.firestore.devices_collection
jobs_collections_name = settings.firestore.jobs_collection
configurations_collection_name = settings.firestore.configurations_collection
configuration_reference_field_path = "configuration_ref"


def pull_tenant_doc(db: firestore.Client, tenant_id: str) -> Optional[firestore.DocumentSnapshot]:
    """Pull the tenant document from the Firestore database, given
    the tenant_id value"""
    tenant_doc = db.collection(tenants_collection_name).where(
        "tenant_id", "==", tenant_id
    ).get()

    if not tenant_doc:
        log.warning(f"Tenant Document with tenant_id: {tenant_id} not found.")
        return None

    return tenant_doc[0]


def pull_current_configuration_from_firestore(
        db: firestore.Client,
        tenant_id: str
) -> firestore.DocumentSnapshot:
    """Pull down from the Firestore DB the most recent configuration document.

    Args:
        db: The instance of a Firestore authenticated client.
        tenant_id (str): The tenant_id value to download the current configuration.

    Returns:
        The configuration firestore.DocumentReference.
    """
    tenant_doc: firestore.DocumentSnapshot = pull_tenant_doc(
        db, tenant_id
    )

    if not tenant_doc:
        log.warning(f"Configuration Document was not found, because "
                    f"Tenant with tenant_id: {tenant_id} not found.")
        return None

    configuration = db.collection(configurations_collection_name).where(
        "tenant_ref", "==", tenant_doc.reference
    ).order_by(
        "server_timestamp", direction=firestore.Query.DESCENDING
    ).limit(1).get()

    if not configuration:
        log.warning("No Configuration document was found.")
        return None

    return configuration[0]


def pull_configuration_from_firestore(db: firestore.Client, configuration_id, tenant_id) -> firestore.DocumentSnapshot:
    """Pull down from the Firestore DB a configuration document given tenant_id and configuration_id.

    Returns:
        The configuration firestore.DocumentReference.
    """

    tenant_doc: firestore.DocumentSnapshot = pull_tenant_doc(db, tenant_id)

    if not tenant_doc:
        log.warning(f"Configuration Document was not found, because "
                    f"Tenant with tenant_id: {tenant_id} not found.")
        return None

    configuration = db.collection(configurations_collection_name). \
        where("tenant_ref", "==", tenant_doc.reference).where(configuration_id_field, "==", configuration_id). \
        limit(1).get()

    if not configuration:
        log.warning("No Configuration document was found.")
        return None

    return configuration[0]


def pull_docs_from_collection_associated_with_configuration(db: firestore.Client,
                                                            collection_name: str,
                                                            configuration_ref: firestore.DocumentReference) -> \
        List[firestore.DocumentSnapshot]:
    """Returns the documents of a collection that has the configuration value equal to
    the configuration reference received.

    Returns:
        The list of documents found for the query.
    """
    documents = db.collection(collection_name).where(configuration_reference_field_path, "==", configuration_ref).get()

    if not documents:
        log.warning(f"No documents found in collection {collection_name} for configuration {configuration_ref.id}")

    return documents


def get_perception_from_firestore(config_id, tenant_id, edge_logical_id, perception_name, client):
    configuration = pull_configuration_from_firestore(client, config_id, tenant_id)
    documents = client.collection(edges_collection_name). \
        where(configuration_reference_field_path, "==", configuration.reference). \
        where("logical_id", "==", edge_logical_id).get()
    if len(documents) != 1:
        return None
    edge_document = documents[0]
    return edge_document.get('perceptions')[perception_name]


def get_edge_from_firestore(config_id, tenant_id, edge_logical_id, client):
    configuration = pull_configuration_from_firestore(client, config_id, tenant_id)
    documents = client.collection(edges_collection_name). \
        where(configuration_reference_field_path, "==", configuration.reference). \
        where("logical_id", "==", edge_logical_id).get()
    if len(documents) != 1:
        return None
    edge_document = documents[0]
    return edge_document


def get_all_tenants_from_firestore(db: firestore.Client):
    documents = db.collection(tenants_collection_name).get()
    return [doc.to_dict() for doc in documents]


def get_machines_from_firestore(db: firestore.Client, tenant_id):
    configuration = pull_current_configuration_from_firestore(db, tenant_id)
    if configuration is None:
        return []
    documents = db.collection(machines_collection_name). \
        where(configuration_reference_field_path, "==", configuration.reference).get()
    return [doc.to_dict() for doc in documents]


def get_machine_from_firestore(db: firestore.Client, tenant_id, machine_id):
    configuration = pull_current_configuration_from_firestore(db, tenant_id)
    documents = db.collection(machines_collection_name). \
        where(configuration_reference_field_path, "==", configuration.reference). \
        where("asset_id", "==", machine_id).get()
    if not documents:
        return None
    return documents[0].to_dict()


def get_machine_from_firestore_by_edge(db: firestore.Client, tenant_id, edge_doc_ref):
    configuration = pull_current_configuration_from_firestore(db, tenant_id)
    logical_id = edge_doc_ref.get().get('logical_id')
    documents = db.collection(machines_collection_name). \
        where(configuration_reference_field_path, "==", configuration.reference). \
        where(u"associated_with_edges", u"array_contains", logical_id).get()
    if not documents:
        return None
    return documents[0].to_dict()


def get_task_from_firestore(db: firestore.Client, tenant_id, machine_id, task_id):
    machine = get_machine_from_firestore(db, tenant_id, machine_id)
    if machine is None or task_id not in machine["tasks"]:
        print(f"Task not found {task_id}")
        return None
    return AssetTask(**machine["tasks"][task_id])


def get_signal_mode_from_firestore(config_id, tenant_id, edge_logical_id, perception_name, client):
    return get_perception_from_firestore(config_id, tenant_id, edge_logical_id, perception_name, client).get('mode', 0)


def get_signal_dimensions_from_firestore(config_id, tenant_id, edge_logical_id, perception_name, client):
    return get_perception_from_firestore(config_id, tenant_id, edge_logical_id, perception_name, client)["dimensions"]



#########################################################
# Below here is the utilitarian code used to generate snapshots and to
# provided firestore data to the Streamlit UI
#########################################################

class ConfigurationSnapshotType(enum.Enum):
    PRELIMINARY = 0
    NORMAL = 1

def _pull_docs_from_collection_associated_with_configuration(
        db: firestore.Client,
        collection_name: str,
        configuration_ref: firestore.DocumentReference,
        as_dict: bool = True,
) -> List[firestore.DocumentSnapshot]:
    """Returns the documents of a collection that has the configuration value equal to
    the configuration reference received.

    Returns:
        The list of documents found for the query.
    """
    documents = (
        db.collection(collection_name)
            .where(configuration_reference_field_path, "==", configuration_ref)
            .get()
    )

    if not documents:
        log.warning(
            f"No documents found in collection {collection_name} for configuration {configuration_ref.id}"
        )

    if as_dict:
        documents = list(map(lambda doc: doc.to_dict(), documents))

    return documents


def pull_project_data_by_date(
        db: firestore.Client, selected_date: datetime.date
) -> "ProjectData":
    """Pulls and returns a project configuration given a date.

    TODO: A Dataclass for the project data should be added in TXP Common
    TODO: If multiple configuration were written on the same day, the return type should
        be a List of that dataclass.
    TODO: Multigateway configuration will pull multiple jobs

    Args:
        db: A configured firestore client instance.
        selected_date: The selected date to perform the query.
    """
    configuration = (
        db.collection(configurations_collection_name)
            .where("since", "<", selected_date)
            .order_by("since", direction=firestore.Query.DESCENDING)
            .limit(1)
            .get()
    )

    if not configuration:
        log.warning(f"No Configuration document was found for date: {selected_date}.")
        return None

    configuration: firestore.DocumentSnapshot = configuration[0]

    machines_groups_documents = (
        _pull_docs_from_collection_associated_with_configuration(
            db, machines_group_collection_name, configuration.reference
        )
    )

    if not machines_groups_documents:
        log.warning(
            "No Machines Groups documents were found associated "
            f"with configuration {configuration.to_dict()['configuration_id']}"
        )
        return None

    machines_documents = _pull_docs_from_collection_associated_with_configuration(
        db, machines_collection_name, configuration.reference
    )

    if not machines_documents:
        log.warning(
            f"No Machines documents were found associated "
            f"with configuration {configuration.to_dict()['configuration_id']}"
        )
        return None

    gateways_documents = _pull_docs_from_collection_associated_with_configuration(
        db, gateways_collection_name, configuration.reference
    )

    if not gateways_documents:
        log.error(
            "No Gateways documents were found associated "
            f"with configuration {configuration.to_dict()['configuration_id']}"
        )
        return None

    edges_documents = _pull_docs_from_collection_associated_with_configuration(
        db, edges_collection_name, configuration.reference
    )

    if not edges_documents:
        log.error(
            "No Edges documents were found associated "
            f"with configuration {configuration.to_dict()['configuration_id']}"
        )
        return None

    devices_documents = _pull_docs_from_collection_associated_with_configuration(
        db, devices_collection_name, configuration.reference
    )

    if not devices_documents:
        log.error(
            "No Devices documents were found associated "
            f"with configuration {configuration.to_dict()['configuration_id']}"
        )
        return None

    job_documents = _pull_docs_from_collection_associated_with_configuration(
        db, jobs_collections_name, configuration.reference
    )

    if not job_documents:
        log.error(
            "No Job documents were found associated with "
            f"with configuration {configuration.to_dict()['configuration_id']}"
        )
        return None

    job_configs: List[JobConfig] = list(
        map(lambda job_dict: JobConfig.build_from_dict(job_dict), job_documents)
    )

    if not any(job_configs):
        log.error(
            "Some/All Job Configurations obtained from Firestore could not be parsed"
        )
        return None

    ret = {
        "last_configuration": configuration,
        "machines_groups": machines_groups_documents,
        "machines": machines_documents,
        "gateways": gateways_documents,
        "edges": edges_documents,
        "devices": devices_documents,
        "jobs": job_documents,
        "query_data": {},
    }

    return ret


def get_authenticated_client(service_account_credentials) -> firestore.Client:
    """Returns a firestore.Client instance, authenticated with the provided
    credentials.

    Args:
        service_account_credentials: A service_account.Credentials object with the
            appropriate permissions to use Firestore.
    """
    return firestore.Client(
        credentials=service_account_credentials,
        project=service_account_credentials.project_id,
    )


def pull_recent_project_data(db: firestore.Client, tenant_id: str) -> "ProjectData":
    """Pulls and returns the project data from the current configuration.

    TODO: A Dataclass for the project data should be added in TXP Common
    TODO: If multiple configuration were written on the same day, the return type should
        be a List of that dataclass.
    TODO: Multigateway configuration will pull multiple jobs

    Args:
        db: A configured firestore client instance.
        tenant_id: The tenant_id to donwload information from.

    # TODO: Delete this function. Use get_current_project_model instead

    """
    configuration = pull_current_configuration_from_firestore(db, tenant_id)

    machines_groups_documents = (
        _pull_docs_from_collection_associated_with_configuration(
            db, machines_group_collection_name, configuration.reference
        )
    )

    if not machines_groups_documents:
        log.warning(
            "No Machines Groups documents were found associated "
            f"with configuration {configuration.to_dict()['configuration_id']}"
        )
        return None

    machines_documents = _pull_docs_from_collection_associated_with_configuration(
        db, machines_collection_name, configuration.reference
    )

    if not machines_documents:
        log.warning(
            f"No Machines documents were found associated "
            f"with configuration {configuration.to_dict()['configuration_id']}"
        )
        return None

    gateways_documents = _pull_docs_from_collection_associated_with_configuration(
        db, gateways_collection_name, configuration.reference
    )

    if not gateways_documents:
        log.error(
            "No Gateways documents were found associated "
            f"with configuration {configuration.to_dict()['configuration_id']}"
        )
        return None

    edges_documents = _pull_docs_from_collection_associated_with_configuration(
        db, edges_collection_name, configuration.reference
    )

    if not edges_documents:
        log.error(
            "No Edges documents were found associated "
            f"with configuration {configuration.to_dict()['configuration_id']}"
        )
        return None

    devices_documents = _pull_docs_from_collection_associated_with_configuration(
        db, devices_collection_name, configuration.reference
    )

    if not devices_documents:
        log.error(
            "No Devices documents were found associated "
            f"with configuration {configuration.to_dict()['configuration_id']}"
        )
        return None

    job_document = _pull_docs_from_collection_associated_with_configuration(
        db, jobs_collections_name, configuration.reference
    )

    if not job_document:
        log.error(
            "No Job document was found associated with "
            f"with configuration {configuration.to_dict()['configuration_id']}"
        )
        return None

    job_document = job_document[0]  # TODO: multigateway configuration
    job_config: JobConfig = JobConfig.build_from_dict(job_document)

    if not job_config:
        log.error("The JobConfig obtained from Firestore could not be parsed")
        return None

    ret = {
        "last_configuration": configuration,
        "machines_groups": machines_groups_documents,
        "machines": machines_documents,
        "gateways": gateways_documents,
        "edges": edges_documents,
        "devices": devices_documents,
        "job": job_document,
        "query_data": {},
    }

    return ret


def _create_devices(
        db: firestore.Client,
        devices: List[Dict],
        configuration_ref: firestore.DocumentReference,
) -> Dict:
    d = {}
    for device_dict in devices:
        log.info(f'Creating device in Firestore: {device_dict["kind"]}')
        device_dict["configuration_ref"] = configuration_ref
        result = db.collection(devices_collection_name).add(device_dict)
        d[device_dict["kind"]] = result[1]
    return d


def _create_edges(
        db: firestore.Client,
        edges_dicts: List[Dict],
        devices_references: Dict[str, firestore.DocumentReference],
        configuration_reference: firestore.DocumentReference,
) -> Dict:
    d = {}
    for edge_dict in edges_dicts:
        log.info(f'Creating edge in Firestore: {edge_dict["logical_id"]}')
        edge_dict["configuration_ref"] = configuration_reference
        edge_dict["is_of_kind_ref"] = devices_references[edge_dict["device_kind"]]
        edge_dict["is_of_kind"] = devices_references[edge_dict["device_kind"]].get().get("kind")
        if "edge_parameters" in edge_dict:
            edge_dict["parameters"] = edge_dict.pop("edge_parameters")
        result = db.collection(edges_collection_name).add(edge_dict)
        d[edge_dict["logical_id"]] = result[1]

    return d


def _create_jobs(
        db: firestore.Client,
        gateway_id_to_job: Dict[str, Dict],
        configuration_ref: firestore.DocumentReference,
) -> Dict:
    d = {}
    for gateway_id, job in gateway_id_to_job.items():
        job["configuration_ref"] = configuration_ref
        result = db.collection(jobs_collections_name).add(job)
        d[gateway_id] = result[1]

    return d


def _create_machines(
        db: firestore.Client,
        machines: List[Dict],
        edges_refs: Dict[str, firestore.DocumentReference],
        configuration_ref: firestore.DocumentReference,
) -> Dict:
    d = {}
    for machine_dict in machines:
        # replace associated_with_edges with edges references
        edges_refs_for_machine = list(
            map(
                lambda edge_logical_id: edges_refs[edge_logical_id],
                machine_dict["edges_ids"],
            )
        )
        edges_refs_for_machine_vals = list(
            map(
                lambda edge_logical_id: edges_refs[edge_logical_id].get().get('edge_logical_id'),
                machine_dict["edges_ids"],
            )
        )
        machine_dict["associated_with_edges"] = edges_refs_for_machine
        machine_dict["associated_with_edges_values"] = edges_refs_for_machine_vals

        machine_dict["configuration_ref"] = configuration_ref

        result = db.collection(machines_collection_name).add(machine_dict)
        d[machine_dict["machine_id"]] = result[1]

    return d


def _create_machines_groups(
        db: firestore.Client,
        machines_groups: List[Dict],
        machines_refs: Dict[str, firestore.DocumentReference],
        configuration_ref: Dict[str, firestore.DocumentReference],
) -> Dict:
    d = {}
    for machine_group_dict in machines_groups:
        machines_docs = list(
            map(
                lambda machine_id: machines_refs[machine_id],
                machine_group_dict["machines"],
            )
        )
        machines_docs_values = list(
            map(
                lambda machine_id: machines_refs[machine_id].get().get('machine_id'),
                machine_group_dict["machines"]
            )
        )

        machine_group_with_machines_refs = {
            **machine_group_dict,
            **{"machines": machines_docs, "configuration_ref": configuration_ref, "machines_values": machines_docs_values},
        }

        result = db.collection(machines_group_collection_name).add(
            machine_group_with_machines_refs
        )
        d[machine_group_dict["name"]] = result[1]

    return d


def _create_gateways(
        db: firestore.Client,
        gateways: List[Dict],
        created_machines: Dict[str, firestore.DocumentReference],
        created_jobs: Dict[str, firestore.DocumentReference],
        configuration_ref: firestore.DocumentReference,
) -> Dict:
    d = {}
    for gateway_dict in gateways:
        gateway_dict["configuration_ref"] = configuration_ref
        gateway_dict["has_job"] = created_jobs[gateway_dict["gateway_id"]]
        gateway_dict["machines"] = list(
            map(lambda machine: created_machines[machine], gateway_dict["machines_ids"])
        )  # list(created_machines.values())
        gateway_dict["machines_val"] = gateway_dict["machines_ids_values"]
        result = db.collection(gateways_collection_name).add(gateway_dict)
        d[gateway_dict["gateway_id"]] = result[1]

    return d


def create_configuration_snapshot(
        db: firestore.Client,
        project_model,
        snapshot_type: ConfigurationSnapshotType,
        tenant_id: str
) -> bool:
    """Creates a new configuration snapshot for the provided project_model

    Returns:
        True if the configuration was created successfully.
    """
    # Pull the tenant document reference to index the configuration
    # Pull the tenant Document
    tenant = db.collection(tenants_collection).where(
        'tenant_id', '==', tenant_id
    ).get()

    if not tenant:
        log.error(f"Tenant document was not found for {tenant_id}")
        return False

    if len(tenant) > 1:
        log.warning(f"Multiple Tenants in the database with id: {tenant_id}.")

    tenant_ref = tenant[0].reference

    #  Creates new configuration
    new_configuration_version: str = (
        txp_config_version.get_next_normal_version(project_model.configuration_version)
        if snapshot_type == ConfigurationSnapshotType.NORMAL
        else txp_config_version.get_next_preliminary_version(
            project_model.configuration_version
        )
    )
    config_timestamp = datetime.datetime.now(
        pytz.timezone(settings.gateway.timezone)
    ).replace(microsecond=0)
    _, new_configuration = db.collection(configurations_collection_name).add(
        {
            "configuration_id": new_configuration_version,
            "since": config_timestamp,
            "server_timestamp": firestore.SERVER_TIMESTAMP,  # TODO: remove this filed if nobody is using it
            "tenant_ref": tenant_ref
        }
    )

    created_devices = {}
    created_edges = {}
    created_jobs = {}
    created_machines = {}
    created_machines_group = {}
    created_gateways = {}

    try:
        created_devices = _create_devices(
            db, list(project_model.device_kinds_table.values()), new_configuration
        )
        log.info("New devices documents created on Snapshot")

        edges = list(
            map(
                lambda edge_descriptor: json.loads(
                    json.dumps(edge_descriptor, cls=ComplexEncoder)
                ),
                list(project_model.edges_table.values()),
            )
        )
        created_edges = _create_edges(db, edges, created_devices, new_configuration)
        log.info("New edges documents created on Snapshot")

        jobs = dict(
            map(
                lambda dict_entry: (
                    dict_entry[0],
                    json.loads(json.dumps(dict_entry[1], cls=ComplexEncoder)),
                ),
                project_model.jobs_table_by_gateway.items(),
            )
        )
        created_jobs = _create_jobs(db, jobs, new_configuration)
        log.info("New jobs documents created on Snapshot")

        machines = list(
            map(
                lambda machine_metadata: json.loads(
                    json.dumps(machine_metadata, cls=ComplexEncoder)
                ),
                list(project_model.machines_table.values()),
            )
        )
        created_machines = _create_machines(
            db, machines, created_edges, new_configuration
        )

        created_machines_group = _create_machines_groups(
            db,
            list(project_model.machines_groups_table.values()),
            created_machines,
            new_configuration,
        )

        gateways = list(
            map(
                lambda gateway_config: json.loads(
                    json.dumps(gateway_config, cls=ComplexEncoder)
                ),
                list(project_model.gateways_table.values()),
            )
        )
        created_gateways = _create_gateways(
            db, gateways, created_machines, created_jobs, new_configuration
        )

    except Exception as e:
        log.error(f"Unknown error while creating documents for new configuration: {e}")
        log.error(traceback.format_exc())
        log.warning(f"Reverting the changes...")
        documents = (
                list(created_devices.values())
                + list(created_edges.values())
                + list(created_jobs.values())
                + list(created_machines.values())
                + list(created_machines_group.values())
                + list(created_gateways.values())
        )
        for document_reference in documents:
            document_reference.delete()
        new_configuration.delete()
        return False

    else:
        log.info("All the new entities were created for the new configuration snapshot")
        return True


def get_sampling_frequency(signal, client):
    configuration = pull_configuration_from_firestore(client, signal["configuration_id"], signal["tenant_id"])
    documents = client.collection(edges_collection_name). \
        where(configuration_reference_field_path, "==", configuration.reference). \
        where("logical_id", "==", signal["edge_logical_id"]).get()
    if len(documents) != 1:
        return 1
    edge_document = documents[0]
    return edge_document.get("perceptions").get(signal["perception_name"]).get("sampling_frequency")


def update_next_section_datetime(db: firestore.Client, tenant_id, section_id, next_date):
    tenant_doc = pull_tenant_doc(db, tenant_id)
    tenant_doc_ref = tenant_doc.reference
    tenant_doc_ref.update({
        f"sections.{section_id}.next": next_date
    })


def update_last_section_datetime(db: firestore.Client, tenant_id, section_id, last_date):
    tenant_doc = pull_tenant_doc(db, tenant_id)
    tenant_doc_ref = tenant_doc.reference
    tenant_doc_ref.update({
        f"sections.{section_id}.last": last_date
    })


def update_last_report_datetime(db: firestore.Client, tenant_id, report_id, last_date):
    tenant_doc = pull_tenant_doc(db, tenant_id)
    tenant_doc_ref = tenant_doc.reference
    tenant_doc_ref.update({
        f"reports.{report_id}.last_generation": last_date
    })
