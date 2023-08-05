from t2iapi.activation_state import types_pb2 as _types_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetAlertActivationRequest(_message.Message):
    __slots__ = ["activation", "handle"]
    ACTIVATION_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    activation: _types_pb2.AlertActivation
    handle: str
    def __init__(self, handle: _Optional[str] = ..., activation: _Optional[_Union[_types_pb2.AlertActivation, str]] = ...) -> None: ...

class SetComponentActivationRequest(_message.Message):
    __slots__ = ["activation", "handle"]
    ACTIVATION_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    activation: _types_pb2.ComponentActivation
    handle: str
    def __init__(self, handle: _Optional[str] = ..., activation: _Optional[_Union[_types_pb2.ComponentActivation, str]] = ...) -> None: ...

class SetSystemSignalActivationRequest(_message.Message):
    __slots__ = ["activation", "handle", "manifestation"]
    ACTIVATION_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    MANIFESTATION_FIELD_NUMBER: _ClassVar[int]
    activation: _types_pb2.AlertActivation
    handle: str
    manifestation: _types_pb2.AlertSignalManifestation
    def __init__(self, handle: _Optional[str] = ..., manifestation: _Optional[_Union[_types_pb2.AlertSignalManifestation, str]] = ..., activation: _Optional[_Union[_types_pb2.AlertActivation, str]] = ...) -> None: ...
