from t2iapi import basic_responses_pb2 as _basic_responses_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CalibrateMetricResponse(_message.Message):
    __slots__ = ["response", "values"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    response: _basic_responses_pb2.BasicResponse
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, response: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., values: _Optional[_Iterable[str]] = ...) -> None: ...

class IsComputerControlledResponse(_message.Message):
    __slots__ = ["answer", "status"]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    answer: bool
    status: _basic_responses_pb2.BasicResponse
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., answer: bool = ...) -> None: ...
