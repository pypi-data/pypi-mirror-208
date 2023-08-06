from .relational_entity import TxpRelationalEntity
from typing import List, Dict
import txp.common.models.protos.models_pb2 as models_pb2
from google.protobuf.json_format import MessageToDict
import dataclasses


@dataclasses.dataclass
class SamplingWindow(TxpRelationalEntity):
    observation_time: int
    sampling_time: int

    @classmethod
    def get_proto_class(cls):
        return models_pb2.SamplingWindowProtob

    @classmethod
    def firestore_collection_name(cls) -> str:
        return ""


@dataclasses.dataclass
class SamplingJobParameters(TxpRelationalEntity):
    active_week_days: str
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    sampling_window: SamplingWindow
    predicates: List[str] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.sampling_window, Dict):
            self.sampling_window = SamplingWindow(**self.sampling_window)


    @classmethod
    def get_proto_class(cls):
        return models_pb2.SamplingJobParametersProto

    @classmethod
    def firestore_collection_name(cls) -> str:
        return ""


@dataclasses.dataclass
class SamplingJobTask(TxpRelationalEntity):
    assets: List[str]
    parameters: SamplingJobParameters

    def __post_init__(self):
        if isinstance(self.parameters, dict):
            self.parameters = SamplingJobParameters(**self.parameters)

    @classmethod
    def firestore_collection_name(cls) -> str:
        return ""

    @classmethod
    def get_proto_class(cls):
        return models_pb2.SamplingJobTaskProto


@dataclasses.dataclass
class SamplingJob(TxpRelationalEntity):
    parameters: SamplingJobParameters
    tasks: List[SamplingJobTask]
    telemetry_rollover_policy: str = "discard"
    job_id: str = ""

    def __post_init__(self):
        if isinstance(self.parameters, dict):
            self.parameters = SamplingJobParameters(**self.parameters)

        for i in range(len(self.tasks)):
            self.tasks[i] = SamplingJobTask(**self.tasks[i])

    @classmethod
    def firestore_collection_name(cls) -> str:
        return "jobs"

    @classmethod
    def get_proto_class(cls):
        return models_pb2.SamplingJobProto
