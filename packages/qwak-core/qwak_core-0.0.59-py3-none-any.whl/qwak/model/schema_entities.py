from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Type

from _qwak_proto.qwak.builds.builds_pb2 import Entity as ProtoEntity
from _qwak_proto.qwak.builds.builds_pb2 import ExplicitFeature as ProtoExplicitFeature
from _qwak_proto.qwak.builds.builds_pb2 import Feature as ProtoFeature
from _qwak_proto.qwak.builds.builds_pb2 import InferenceOutput as ProtoInferenceOutput
from _qwak_proto.qwak.builds.builds_pb2 import Prediction as ProtoPrediction
from _qwak_proto.qwak.builds.builds_pb2 import RequestInput as ProtoRequestInput
from _qwak_proto.qwak.builds.builds_pb2 import SourceFeature as ProtoSourceFeature
from _qwak_proto.qwak.builds.builds_pb2 import ValueType


@dataclass(unsafe_hash=True)
class Entity:
    name: str
    type: Type = str

    def to_proto(self):
        return ProtoEntity(
            name=self.name, type=ValueType(type=_type_conversion(self.type))
        )


@dataclass
class BaseFeature(ABC):
    name: str

    @abstractmethod
    def to_proto(self):
        pass


@dataclass(unsafe_hash=True)
class ExplicitFeature(BaseFeature):
    type: Type

    def to_proto(self):
        return ProtoFeature(
            explicit_feature=ProtoExplicitFeature(
                name=self.name, type=ValueType(type=_type_conversion(self.type))
            )
        )

    def to_source_proto(self):
        return ProtoSourceFeature(
            explicit_feature=ProtoExplicitFeature(
                name=self.name, type=ValueType(type=_type_conversion(self.type))
            )
        )


@dataclass(unsafe_hash=True)
class RequestInput(BaseFeature):
    type: Type

    def to_proto(self):
        return ProtoFeature(
            request_input=ProtoRequestInput(
                name=self.name, type=ValueType(type=_type_conversion(self.type))
            )
        )

    def to_source_proto(self):
        return ProtoSourceFeature(
            request_input=ProtoRequestInput(
                name=self.name, type=ValueType(type=_type_conversion(self.type))
            )
        )


@dataclass(unsafe_hash=True)
class FeatureStoreInput(BaseFeature):
    entity: Entity
    type: Optional[str] = None

    def to_proto(self):
        pass


@dataclass(unsafe_hash=True)
class InferenceOutput:
    name: str
    type: type

    def to_proto(self):
        return ProtoInferenceOutput(
            name=self.name, type=ValueType(type=_type_conversion(self.type))
        )


@dataclass(unsafe_hash=True)
class Prediction:
    name: str
    type: type

    def to_proto(self):
        return ProtoPrediction(
            name=self.name, type=ValueType(type=_type_conversion(self.type))
        )


def _type_conversion(type):
    if type == int:
        return ValueType.INT32
    elif type == str:
        return ValueType.STRING
    elif type == bytes:
        return ValueType.BYTES
    elif type == bool:
        return ValueType.BOOL
    elif type == float:
        return ValueType.FLOAT
