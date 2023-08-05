from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor
OPERATING_MODE_DISABLED: OperatingMode
OPERATING_MODE_ENABLED: OperatingMode
OPERATING_MODE_NOT_AVAILABLE: OperatingMode

class OperatingMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
