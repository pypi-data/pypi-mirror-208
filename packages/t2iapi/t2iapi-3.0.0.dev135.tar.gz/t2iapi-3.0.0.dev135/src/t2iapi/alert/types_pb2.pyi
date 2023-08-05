from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

ALARM_SIGNAL_INACTIVATION_STATE_DISABLED: AlarmSignalInactivationState
ALARM_SIGNAL_INACTIVATION_STATE_ENABLED: AlarmSignalInactivationState
ALERT_CONDITION_ESCALATION_PROCESS_START_DEESCALATION: AlertConditionEscalationProcess
ALERT_CONDITION_ESCALATION_PROCESS_START_ESCALATION: AlertConditionEscalationProcess
ALERT_CONDITION_ESCALATION_PROCESS_STOP_DEESCALATION: AlertConditionEscalationProcess
ALERT_CONDITION_ESCALATION_PROCESS_STOP_ESCALATION: AlertConditionEscalationProcess
ALERT_CONDITION_PRESENCE_FALSE: AlertConditionPresence
ALERT_CONDITION_PRESENCE_TRUE: AlertConditionPresence
ALERT_SIGNAL_PRESENCE_ACK: AlertSignalPresence
ALERT_SIGNAL_PRESENCE_LATCH: AlertSignalPresence
ALERT_SIGNAL_PRESENCE_OFF: AlertSignalPresence
ALERT_SIGNAL_PRESENCE_ON: AlertSignalPresence
DESCRIPTOR: _descriptor.FileDescriptor

class AlertSignalPresence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class AlertConditionEscalationProcess(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class AlarmSignalInactivationState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class AlertConditionPresence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
