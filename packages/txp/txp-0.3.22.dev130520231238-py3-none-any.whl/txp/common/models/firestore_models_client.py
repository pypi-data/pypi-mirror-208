"""
This file defines a parallel firestore.Client wrapper designed
to be used by the server side code that requires to access the
Firestore DB model of a TXP tenant deployment.
"""
import google.cloud.firestore as firestore
from google.oauth2 import service_account
from typing import List, Tuple, Union
from .relational_entity import TxpRelationalEntity
import logging
from txp.common.config import settings
import dataclasses
import time
from concurrent.futures import ThreadPoolExecutor, wait
log = logging.getLogger(__name__)
log.setLevel(settings.txp.general_log_level)


@dataclasses.dataclass
class FirestoreModelsQuery:
    model_ref: TxpRelationalEntity
    tenant_id: str
    query_operators: List[Tuple[str, str, str]] = dataclasses.field(default_factory=list)
    fields: List[str] = dataclasses.field(default_factory=list)
    collection_path: str = None
    require_conf_ref: bool = True

    def __post_init__(self):
        if not self.collection_path:
            self.collection_path = self.model_ref.firestore_collection_name()


class FirestoreModelsClient:
    def __init__(
        self,
        credentials: service_account.Credentials
    ):
        if credentials is not None:
            self._client: firestore.Client = firestore.Client(
                credentials=credentials
            )
        else:
            self._client: firestore.Client = firestore.Client(
                credentials=credentials
            )
        self._queries: List[FirestoreModelsQuery] = []
        logging.debug(f"{self.__class__.__name__} successfully created")

    def add_query(
        self, q: Union[FirestoreModelsQuery, List[FirestoreModelsQuery]]
    ):
        logging.info(f"{self.__class__.__name__} appended new query to be executed")
        if type(q) == list:
            self._queries += q
        else:
            self._queries.append(q)

    def get_query_results(self) -> List[List[TxpRelationalEntity]]:
        configuration_ref = self._pull_firestore_tenant_configuration(self._queries[0].tenant_id).reference
        start = time.time()
        pool = ThreadPoolExecutor()
        futures = []
        for q in self._queries:
            futures.append(
                pool.submit(
                    self._process_query,
                    q, configuration_ref
                )
            )
        wait(futures)
        query_results = list(map(
            lambda f: f.result(), futures
        ))
        end = time.time()
        log.info(f"Total time downloading documents from firestore {end-start} secs")
        return query_results


    ############################ Util Methods ############################
    def _process_query(self, q: FirestoreModelsQuery, configuration_ref: firestore.DocumentReference):
        query_build = self._client.collection(q.collection_path)
        if q.require_conf_ref:
            query_build = query_build.where("configuration_ref", "==", configuration_ref)
        for op in q.query_operators:
            query_build = query_build.where(op[0], op[1], op[2])
        if q.fields:
            query_build = query_build.select(q.fields)
        documents_snapshots = query_build.get()
        # Maps the plain dicts to protos
        documents_protos = list(map(
            lambda d: q.model_ref.get_proto_from_dict(d.to_dict()),
            documents_snapshots
        ))

        # Maps to instances of the class
        entities = list(map(
            lambda p: q.model_ref.get_instance_from_proto(p),
            documents_protos
        ))

        return entities


    def _pull_tenant_document(self, tenant_id):
        tenant_doc = self._client.collection("tenants").where(
            "tenant_id", "==", tenant_id
        ).get()
        if not tenant_doc:
            log.warning(f"Tenant Document with tenant_id: {tenant_id} not found.")
            return None
        tenant_doc = tenant_doc[0]
        return tenant_doc

    def _pull_firestore_tenant_configuration(self, tenant_id: str):
        tenant_doc = self._pull_tenant_document(tenant_id)
        configuration = self._client.collection("configurations").where(
            "tenant_ref", "==", tenant_doc.reference
        ).order_by(
            "server_timestamp", direction=firestore.Query.DESCENDING
        ).limit(1).get()
        if not configuration:
            log.warning("No Configuration document was found.")
            return None
        return configuration[0]





