from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor
GENERATION_MODE_DEMO: GenerationMode
GENERATION_MODE_REAL: GenerationMode
GENERATION_MODE_TEST: GenerationMode
MEASUREMENT_VALIDITY_CALIBRATION_ONGOING: MeasurementValidity
MEASUREMENT_VALIDITY_INVALID: MeasurementValidity
MEASUREMENT_VALIDITY_MEASUREMENT_ONGOING: MeasurementValidity
MEASUREMENT_VALIDITY_NA: MeasurementValidity
MEASUREMENT_VALIDITY_OVERFLOW: MeasurementValidity
MEASUREMENT_VALIDITY_QUESTIONABLE: MeasurementValidity
MEASUREMENT_VALIDITY_UNDERFLOW: MeasurementValidity
MEASUREMENT_VALIDITY_VALID: MeasurementValidity
MEASUREMENT_VALIDITY_VALIDATED_DATA: MeasurementValidity
METRIC_STATUS_CURRENTLY_DE_INITIALIZING: MetricStatus
METRIC_STATUS_CURRENTLY_INITIALIZING: MetricStatus
METRIC_STATUS_DE_INITIALIZED_AND_NOT_PERFORMING_OR_APPLYING: MetricStatus
METRIC_STATUS_FAILED: MetricStatus
METRIC_STATUS_INITIALIZED_BUT_NOT_PERFORMING_OR_APPLYING: MetricStatus
METRIC_STATUS_PERFORMED_OR_APPLIED: MetricStatus
OPERATION_MODE_STATUS_OFF: OperationModeStatus
OPERATION_MODE_STATUS_ON: OperationModeStatus
OPERATION_MODE_STATUS_PAUSED: OperationModeStatus

class MeasurementValidity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class GenerationMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class OperationModeStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class MetricStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
