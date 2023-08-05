from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
DESCRIPTOR_CLASS_ABSTRACT: DescriptorClass
DESCRIPTOR_CLASS_MDS: DescriptorClass
MDS_OPERATING_MODE_DEMO: MdsOperatingMode
MDS_OPERATING_MODE_MAINTENANCE: MdsOperatingMode
MDS_OPERATING_MODE_NORMAL: MdsOperatingMode
MDS_OPERATING_MODE_SERVICE: MdsOperatingMode
REPORT_TYPE_DESCRIPTION_MODIFICATION_REPORT: ReportType
REPORT_TYPE_EPISODIC_ALERT_REPORT: ReportType
REPORT_TYPE_EPISODIC_COMPONENT_REPORT: ReportType
REPORT_TYPE_EPISODIC_CONTEXT_REPORT: ReportType
REPORT_TYPE_EPISODIC_METRIC_REPORT: ReportType
REPORT_TYPE_EPISODIC_OPERATIONAL_STATE_REPORT: ReportType
REPORT_TYPE_OBSERVED_VALUE_STREAM: ReportType
REPORT_TYPE_OPERATION_INVOKED_REPORT: ReportType
REPORT_TYPE_PERIODIC_ALERT_REPORT: ReportType
REPORT_TYPE_PERIODIC_COMPONENT_REPORT: ReportType
REPORT_TYPE_PERIODIC_CONTEXT_REPORT: ReportType
REPORT_TYPE_PERIODIC_METRIC_REPORT: ReportType
REPORT_TYPE_PERIODIC_OPERATIONAL_STATE_REPORT: ReportType
REPORT_TYPE_SYSTEM_ERROR_REPORT: ReportType
REPORT_TYPE_WAVEFORM_STREAM: ReportType

class ExpandedName(_message.Message):
    __slots__ = ["local_name", "uri"]
    LOCAL_NAME_FIELD_NUMBER: _ClassVar[int]
    URI_FIELD_NUMBER: _ClassVar[int]
    local_name: str
    uri: _wrappers_pb2.StringValue
    def __init__(self, uri: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., local_name: _Optional[str] = ...) -> None: ...

class ReportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class MdsOperatingMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DescriptorClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
