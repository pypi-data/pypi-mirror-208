from .relational_entity import TxpRelationalEntity
from typing import List, Dict
from .device import *
import txp.common.models.protos.models_pb2 as models_pb2
import dataclasses


@dataclasses.dataclass
class Edge(TxpRelationalEntity):
    logical_id: str
    type: str = ""
    device_kind: str = ""
    parameters: DeviceParameters = dataclasses.field(default_factory=dict)
    perceptions: Dict[str, Perception] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.parameters, dict):
            self.parameters = DeviceParameters(**self.parameters)

        for k, v in self.perceptions.copy().items():
            if isinstance(v, Dict):
                self.perceptions[k] = Perception(**v)

    @classmethod
    def firestore_collection_name(cls) -> str:
        return "edges"

    @classmethod
    def get_proto_class(cls):
        return models_pb2.EdgeProto
