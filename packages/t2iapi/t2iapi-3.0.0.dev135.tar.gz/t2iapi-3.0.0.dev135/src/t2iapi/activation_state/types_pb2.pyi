from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

ALERT_ACTIVATION_OFF: AlertActivation
ALERT_ACTIVATION_ON: AlertActivation
ALERT_ACTIVATION_PSD: AlertActivation
ALERT_SIGNAL_MANIFESTATION_AUD: AlertSignalManifestation
ALERT_SIGNAL_MANIFESTATION_OTH: AlertSignalManifestation
ALERT_SIGNAL_MANIFESTATION_TAN: AlertSignalManifestation
ALERT_SIGNAL_MANIFESTATION_VIS: AlertSignalManifestation
COMPONENT_ACTIVATION_FAILURE: ComponentActivation
COMPONENT_ACTIVATION_NOT_READY: ComponentActivation
COMPONENT_ACTIVATION_OFF: ComponentActivation
COMPONENT_ACTIVATION_ON: ComponentActivation
COMPONENT_ACTIVATION_SHUTDOWN: ComponentActivation
COMPONENT_ACTIVATION_STANDBY: ComponentActivation
DESCRIPTOR: _descriptor.FileDescriptor

class ComponentActivation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class AlertActivation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class AlertSignalManifestation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
