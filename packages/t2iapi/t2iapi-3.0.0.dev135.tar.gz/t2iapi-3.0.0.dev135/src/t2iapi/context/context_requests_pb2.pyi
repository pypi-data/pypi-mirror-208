from t2iapi.context import types_pb2 as _types_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AssociatePatientRequest(_message.Message):
    __slots__ = ["patient_type"]
    PATIENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    patient_type: _types_pb2.PatientType
    def __init__(self, patient_type: _Optional[_Union[_types_pb2.PatientType, str]] = ...) -> None: ...

class ContextStateHandleRequest(_message.Message):
    __slots__ = ["context_state_handle"]
    CONTEXT_STATE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    context_state_handle: str
    def __init__(self, context_state_handle: _Optional[str] = ...) -> None: ...

class CreateContextStateWithAssocAndSpecificValidatorRequest(_message.Message):
    __slots__ = ["context_association", "descriptor_handle", "validator_type"]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    context_association: _types_pb2.ContextAssociation
    descriptor_handle: str
    validator_type: _types_pb2.ValidatorType
    def __init__(self, descriptor_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ..., validator_type: _Optional[_Union[_types_pb2.ValidatorType, str]] = ...) -> None: ...

class CreateContextStateWithAssociationAndValidatorsRequest(_message.Message):
    __slots__ = ["context_association", "descriptor_handle", "num_validators"]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    NUM_VALIDATORS_FIELD_NUMBER: _ClassVar[int]
    context_association: _types_pb2.ContextAssociation
    descriptor_handle: str
    num_validators: str
    def __init__(self, descriptor_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ..., num_validators: _Optional[str] = ...) -> None: ...

class CreateContextStateWithAssociationRequest(_message.Message):
    __slots__ = ["context_association", "descriptor_handle"]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    context_association: _types_pb2.ContextAssociation
    descriptor_handle: str
    def __init__(self, descriptor_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ...) -> None: ...

class SetContextStateAssociationRequest(_message.Message):
    __slots__ = ["context_association", "context_state_handle", "descriptor_handle"]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_STATE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    context_association: _types_pb2.ContextAssociation
    context_state_handle: str
    descriptor_handle: str
    def __init__(self, descriptor_handle: _Optional[str] = ..., context_state_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ...) -> None: ...

class SetLocationDetailRequest(_message.Message):
    __slots__ = ["location"]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    location: _types_pb2.LocationDetail
    def __init__(self, location: _Optional[_Union[_types_pb2.LocationDetail, _Mapping]] = ...) -> None: ...
