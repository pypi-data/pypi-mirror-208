from typing import List

from datagen_protocol.schema.attributes import Generator
from datagen_protocol.schema.base import SchemaBaseModel
from datagen_protocol.schema.hic.sequence import DataSequence
from datagen_protocol.schema.humans import HumanDatapoint


class GenerationRequest(SchemaBaseModel):
    generator: Generator


class DataRequest(GenerationRequest):
    generator: Generator = Generator.IDENTITIES
    datapoints: List[HumanDatapoint]

    def __len__(self):
        return len(self.datapoints)


class SequenceRequest(GenerationRequest):
    generator: Generator = Generator.HIC
    sequences: List[DataSequence]

    def __len__(self):
        return len(self.sequences)
