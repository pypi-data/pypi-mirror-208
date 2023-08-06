from .relational_entity import TxpRelationalEntity
from typing import List, Dict, Optional
import txp.common.models.protos.models_pb2 as models_pb2
from google.protobuf.json_format import MessageToDict
from .perception import Perception
import dataclasses


@dataclasses.dataclass
class PhysicalSensor(TxpRelationalEntity):
    camera_type: str
    physical_id: str

    @classmethod
    def get_proto_class(cls):
        return models_pb2.PhysicalSensorProto

    @classmethod
    def firestore_collection_name(cls) -> str:
        return "" # Not own collection. Is a field


@dataclasses.dataclass
class VirtualDevice(TxpRelationalEntity):
    position: List[int] = dataclasses.field(default_factory=list)
    virtual_id_hash: str = ""

    @classmethod
    def get_proto_class(cls):
        return models_pb2.VirtualDeviceProto

    @classmethod
    def firestore_collection_name(cls) -> str:
        return "" # Not own collection. It's a field


@dataclasses.dataclass
class DeviceParameters(TxpRelationalEntity):
    physical_id: str = ""
    sensors: Optional[List[PhysicalSensor]] = None
    virtual_device: Optional[VirtualDevice] = None

    def __post_init__(self):
        if isinstance(self.virtual_device, dict):
            self.virtual_device = VirtualDevice(**self.virtual_device)

        if self.sensors:
            for i in range(len(self.sensors)):
                if isinstance(self.sensors[i], dict):
                    self.sensors[i] = PhysicalSensor(**self.sensors[i])

    @classmethod
    def get_proto_class(cls):
        return models_pb2.DeviceParametersProto

    @classmethod
    def firestore_collection_name(cls) -> str:
        return "" # Not own collection. It's a field


@dataclasses.dataclass
class Device(TxpRelationalEntity):
    kind: str
    type: str
    parameters: DeviceParameters = dataclasses.field(default_factory=DeviceParameters)
    perceptions: Dict[str, Perception] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.parameters, dict):
            self.parameters = DeviceParameters(**self.parameters)

        for k, v in self.perceptions.copy().items():
            if isinstance(v, Dict):
                self.perceptions[k] = Perception(**v)

    @classmethod
    def get_proto_class(cls):
        return models_pb2.DeviceProto

    @classmethod
    def firestore_collection_name(cls) -> str:
        return "devices"
