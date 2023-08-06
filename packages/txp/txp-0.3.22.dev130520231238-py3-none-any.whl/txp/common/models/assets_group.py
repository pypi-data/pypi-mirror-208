from .relational_entity import TxpRelationalEntity
from typing import List, Dict
import txp.common.models.protos.models_pb2 as models_pb2
import dataclasses


@dataclasses.dataclass
class AssetsGroup(TxpRelationalEntity):
    name: str = ""
    address: str = ""
    assets: List[str] = ""

    @classmethod
    def firestore_collection_name(cls) -> str:
        return "assets_groups"  # TODO: change this to `assets_groups`

    @classmethod
    def get_proto_class(cls):
        return models_pb2.AssetsGroupProto
