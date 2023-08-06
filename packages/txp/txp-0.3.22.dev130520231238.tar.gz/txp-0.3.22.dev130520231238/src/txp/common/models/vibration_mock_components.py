from .relational_entity import TxpRelationalEntity
from typing import List, Dict
import txp.common.models.protos.models_pb2 as models_pb2
import dataclasses


@dataclasses.dataclass
class VibrationMockComponent(TxpRelationalEntity):
    """This entity represents a component from the MockDriver configuration."""
    amplitude: int = 1
    component_type: str = "sine"
    frequency: int = 100
    phase: int = 1

    @classmethod
    def firestore_collection_name(cls) -> str:
        return ""  # It's a field inside a parent document

    @classmethod
    def get_proto_class(cls):
        return models_pb2.VibrationMockComponentsProto
