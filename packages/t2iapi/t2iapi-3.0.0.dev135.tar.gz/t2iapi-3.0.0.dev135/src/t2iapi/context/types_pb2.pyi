from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

CONTEXT_ASSOCIATION_ASSOCIATED: ContextAssociation
CONTEXT_ASSOCIATION_DISASSOCIATED: ContextAssociation
CONTEXT_ASSOCIATION_NOT_ASSOCIATED: ContextAssociation
CONTEXT_ASSOCIATION_PRE_ASSOCIATED: ContextAssociation
CONTEXT_TYPE_ENSEMBLE: ContextType
CONTEXT_TYPE_LOCATION: ContextType
CONTEXT_TYPE_MEANS: ContextType
CONTEXT_TYPE_OPERATOR: ContextType
CONTEXT_TYPE_PATIENT: ContextType
CONTEXT_TYPE_WORKFLOW: ContextType
DESCRIPTOR: _descriptor.FileDescriptor
PATIENT_TYPE_ADOLESCENT: PatientType
PATIENT_TYPE_ADULT: PatientType
PATIENT_TYPE_INFANT: PatientType
PATIENT_TYPE_NEONATAL: PatientType
PATIENT_TYPE_OTHER: PatientType
PATIENT_TYPE_PEDIATRIC: PatientType
PATIENT_TYPE_UNSPECIFIED: PatientType
VALIDATOR_TYPE_BIOMED: ValidatorType
VALIDATOR_TYPE_CLINICAL_SUPER_USER: ValidatorType
VALIDATOR_TYPE_REMOTE_SERVICE_OPERATION: ValidatorType
VALIDATOR_TYPE_SERVICE_PERSONNEL: ValidatorType
VALIDATOR_TYPE_TECHNICAL_MEANS: ValidatorType
VALIDATOR_TYPE_USER: ValidatorType

class LocationDetail(_message.Message):
    __slots__ = ["bed", "building", "facility", "floor", "poc", "room"]
    BED_FIELD_NUMBER: _ClassVar[int]
    BUILDING_FIELD_NUMBER: _ClassVar[int]
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    FLOOR_FIELD_NUMBER: _ClassVar[int]
    POC_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    bed: _wrappers_pb2.StringValue
    building: _wrappers_pb2.StringValue
    facility: _wrappers_pb2.StringValue
    floor: _wrappers_pb2.StringValue
    poc: _wrappers_pb2.StringValue
    room: _wrappers_pb2.StringValue
    def __init__(self, poc: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., room: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., bed: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., facility: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., building: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., floor: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...

class ContextAssociation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class PatientType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ValidatorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ContextType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
