from t2iapi.device import types_pb2 as _types_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChangeMdibSequenceIdRequest(_message.Message):
    __slots__ = ["descriptive_name"]
    DESCRIPTIVE_NAME_FIELD_NUMBER: _ClassVar[int]
    descriptive_name: str
    def __init__(self, descriptive_name: _Optional[str] = ...) -> None: ...

class GetRemovableDescriptorsOfClassRequest(_message.Message):
    __slots__ = ["descriptor_class"]
    DESCRIPTOR_CLASS_FIELD_NUMBER: _ClassVar[int]
    descriptor_class: _types_pb2.DescriptorClass
    def __init__(self, descriptor_class: _Optional[_Union[_types_pb2.DescriptorClass, str]] = ...) -> None: ...

class SetDeviceOperatingModeRequest(_message.Message):
    __slots__ = ["mode"]
    MODE_FIELD_NUMBER: _ClassVar[int]
    mode: _types_pb2.MdsOperatingMode
    def __init__(self, mode: _Optional[_Union[_types_pb2.MdsOperatingMode, str]] = ...) -> None: ...

class SetLanguageRequest(_message.Message):
    __slots__ = ["language"]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    language: str
    def __init__(self, language: _Optional[str] = ...) -> None: ...

class TriggerReportRequest(_message.Message):
    __slots__ = ["report"]
    REPORT_FIELD_NUMBER: _ClassVar[int]
    report: _types_pb2.ReportType
    def __init__(self, report: _Optional[_Union[_types_pb2.ReportType, str]] = ...) -> None: ...
