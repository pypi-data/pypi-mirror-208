from .relational_entity import TxpRelationalEntity
from typing import List, Dict
import txp.common.models.protos.models_pb2 as models_pb2
import dataclasses


@dataclasses.dataclass
class Gateway(TxpRelationalEntity):
    gateway_id: str = ""
    cloud_region: str = ""
    assets: List[str] = ""
    project_id: str = ""
    registry_id: str = ""
    has_job: str = ""
    tenant_id: str = ""

    @classmethod
    def get_proto_class(cls):
        return models_pb2.GatewayProto

    @classmethod
    def firestore_collection_name(cls) -> str:
        return "gateways"
