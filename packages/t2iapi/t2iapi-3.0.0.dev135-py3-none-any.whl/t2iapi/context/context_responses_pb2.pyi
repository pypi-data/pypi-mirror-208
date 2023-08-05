from t2iapi import basic_responses_pb2 as _basic_responses_pb2
from t2iapi import response_types_pb2 as _response_types_pb2
from t2iapi.context import types_pb2 as _types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateContextStateWithAssociationAndUniqueIdentificationResponse(_message.Message):
    __slots__ = ["context_state_handle", "extension", "root", "status"]
    CONTEXT_STATE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    ROOT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    context_state_handle: str
    extension: str
    root: str
    status: _basic_responses_pb2.BasicResponse
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., context_state_handle: _Optional[str] = ..., extension: _Optional[str] = ..., root: _Optional[str] = ...) -> None: ...

class CreateContextStateWithAssociationResponse(_message.Message):
    __slots__ = ["context_state_handle", "status"]
    CONTEXT_STATE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    context_state_handle: str
    status: _basic_responses_pb2.BasicResponse
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., context_state_handle: _Optional[str] = ...) -> None: ...

class EnsembleContextIndicateMembershipWithIdentificationResponse(_message.Message):
    __slots__ = ["identification", "status"]
    IDENTIFICATION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    identification: _containers.RepeatedCompositeFieldContainer[_response_types_pb2.PartialInstanceIdentifier]
    status: _basic_responses_pb2.BasicResponse
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., identification: _Optional[_Iterable[_Union[_response_types_pb2.PartialInstanceIdentifier, _Mapping]]] = ...) -> None: ...

class GetSupportedContextTypesResponse(_message.Message):
    __slots__ = ["context_type", "status"]
    CONTEXT_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    context_type: _containers.RepeatedScalarFieldContainer[_types_pb2.ContextType]
    status: _basic_responses_pb2.BasicResponse
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., context_type: _Optional[_Iterable[_Union[_types_pb2.ContextType, str]]] = ...) -> None: ...
