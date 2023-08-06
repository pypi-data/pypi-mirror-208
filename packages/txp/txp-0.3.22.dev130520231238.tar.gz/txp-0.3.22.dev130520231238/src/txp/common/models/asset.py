from .relational_entity import TxpRelationalEntity
from typing import List, Dict
import txp.common.models.protos.models_pb2 as models_pb2
import dataclasses


@dataclasses.dataclass
class Asset(TxpRelationalEntity):
    asset_id: str = ""
    state_manager: str = ""
    associated_with_edges: List[str] = dataclasses.field(default_factory=list)
    tasks: Dict = dataclasses.field(default_factory=dict)

    @classmethod
    def firestore_collection_name(cls) -> str:
        return "assets"  # TODO: change name to `assets`

    @classmethod
    def get_proto_class(cls):
        return models_pb2.AssetProto
