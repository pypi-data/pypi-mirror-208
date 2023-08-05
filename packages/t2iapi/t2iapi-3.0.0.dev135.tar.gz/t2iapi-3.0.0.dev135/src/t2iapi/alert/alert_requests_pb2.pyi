from t2iapi.alert import types_pb2 as _types_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AlertConditionEscalationRequest(_message.Message):
    __slots__ = ["escalation_process", "handle"]
    ESCALATION_PROCESS_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    escalation_process: _types_pb2.AlertConditionEscalationProcess
    handle: str
    def __init__(self, handle: _Optional[str] = ..., escalation_process: _Optional[_Union[_types_pb2.AlertConditionEscalationProcess, str]] = ...) -> None: ...

class SetAlarmSignalInactivationStateRequest(_message.Message):
    __slots__ = ["enable", "handle"]
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    enable: _types_pb2.AlarmSignalInactivationState
    handle: str
    def __init__(self, handle: _Optional[str] = ..., enable: _Optional[_Union[_types_pb2.AlarmSignalInactivationState, str]] = ...) -> None: ...

class SetAlertConditionPresenceRequest(_message.Message):
    __slots__ = ["handle", "presence"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    handle: str
    presence: bool
    def __init__(self, handle: _Optional[str] = ..., presence: bool = ...) -> None: ...

class SetAlertSignalPresenceRequest(_message.Message):
    __slots__ = ["handle", "presence"]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    handle: str
    presence: _types_pb2.AlertSignalPresence
    def __init__(self, handle: _Optional[str] = ..., presence: _Optional[_Union[_types_pb2.AlertSignalPresence, str]] = ...) -> None: ...
