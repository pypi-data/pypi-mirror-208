from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor
TASK_STATUS_CANCELLED: TaskStatus
TASK_STATUS_CANCELLING: TaskStatus
TASK_STATUS_COMPLETED: TaskStatus
TASK_STATUS_CREATING: TaskStatus
TASK_STATUS_DISPATCHED: TaskStatus
TASK_STATUS_ERROR: TaskStatus
TASK_STATUS_PROCESSED: TaskStatus
TASK_STATUS_PROCESSING: TaskStatus
TASK_STATUS_RETRIED: TaskStatus
TASK_STATUS_SUBMITTED: TaskStatus
TASK_STATUS_TIMEOUT: TaskStatus
TASK_STATUS_UNSPECIFIED: TaskStatus

class TaskStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
