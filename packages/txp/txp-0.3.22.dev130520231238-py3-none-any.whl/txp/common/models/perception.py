from .relational_entity import TxpRelationalEntity
from .vibration_mock_components import VibrationMockComponent
from typing import List, Dict, Optional
import txp.common.models.protos.models_pb2 as models_pb2
from google.protobuf.json_format import MessageToDict
import dataclasses


@dataclasses.dataclass
class Perception(TxpRelationalEntity):
    """This entity represents a Perception Dimension captured
    by an edge device"""
    name: models_pb2.PerceptionNameEnum = models_pb2.Invalid
    mode: int = 0
    sampling_frequency: Optional[int] = 0
    resolution: Optional[List] = None   # Image Resolution
    dimensions: Optional[List] = None   # Raw Signals Dimensions
    format: Optional[str] = None        # Image format to capture
    components_per_dimension: Optional[List[VibrationMockComponent]] = dataclasses.field(default_factory=list) # VibrationMock Perception field

    def __post_init__(self):
        if self.components_per_dimension:
            for i in range(len(self.components_per_dimension)):
                if isinstance(self.components_per_dimension[i], dict):
                    self.components_per_dimension[i] = VibrationMockComponent(
                        **self.components_per_dimension[i]
                    )

    @classmethod
    def firestore_collection_name(cls) -> str:
        return ""  # It's a field inside a parent document

    @classmethod
    def get_proto_class(cls):
        return models_pb2.PerceptionProto
