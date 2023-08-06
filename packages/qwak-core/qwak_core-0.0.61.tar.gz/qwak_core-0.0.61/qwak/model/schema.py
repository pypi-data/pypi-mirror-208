from dataclasses import dataclass, field
from typing import List

from _qwak_proto.qwak.builds.builds_pb2 import ModelSchema as ProtoModelSchema
from qwak.model.schema_entities import (
    BaseFeature,
    Entity,
    ExplicitFeature,
    FeatureStoreInput,
    InferenceOutput,
)

__all__ = ["ModelSchema", "ExplicitFeature", "InferenceOutput", "FeatureStoreInput"]


@dataclass
class ModelSchema:
    entities: List[Entity] = field(default_factory=list)
    inputs: List[BaseFeature] = field(default_factory=list)
    outputs: List[InferenceOutput] = field(default_factory=list)

    def to_proto(self):
        return ProtoModelSchema(
            entities=[entity.to_proto() for entity in self.entities],
            features=[feature.to_proto() for feature in self.inputs],
            inference_output=[inference.to_proto() for inference in self.outputs],
        )
