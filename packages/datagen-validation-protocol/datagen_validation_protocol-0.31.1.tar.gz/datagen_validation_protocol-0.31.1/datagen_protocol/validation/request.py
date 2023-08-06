from typing import List

from datagen_protocol.schema import request as core_request_schema
from datagen_protocol.validation.hic.sequence import DataSequence as ValidationDataSequence
from datagen_protocol.validation.humans.human import HumanDatapoint as ValidationHumanDatapoint


class DataRequest(core_request_schema.DataRequest):
    datapoints: List[ValidationHumanDatapoint]


class SequenceRequest(core_request_schema.SequenceRequest):
    sequences: List[ValidationDataSequence]


core_request_schema.DataRequest = DataRequest
core_request_schema.SequenceRequest = SequenceRequest
