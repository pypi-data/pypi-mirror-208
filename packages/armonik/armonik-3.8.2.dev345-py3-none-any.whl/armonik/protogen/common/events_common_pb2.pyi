from . import result_status_pb2 as _result_status_pb2
from . import task_status_pb2 as _task_status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventSubscriptionRequest(_message.Message):
    __slots__ = ["session_id"]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class EventSubscriptionResponse(_message.Message):
    __slots__ = ["new_result", "new_task", "result_owner_update", "result_status_update", "session_id", "task_status_update"]
    class NewResult(_message.Message):
        __slots__ = ["owner_id", "result_id", "status"]
        OWNER_ID_FIELD_NUMBER: _ClassVar[int]
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        owner_id: str
        result_id: str
        status: _result_status_pb2.ResultStatus
        def __init__(self, result_id: _Optional[str] = ..., owner_id: _Optional[str] = ..., status: _Optional[_Union[_result_status_pb2.ResultStatus, str]] = ...) -> None: ...
    class NewTask(_message.Message):
        __slots__ = ["data_dependencies", "expected_output_keys", "origin_task_id", "payload_id", "retry_of_ids", "status", "task_id"]
        DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
        EXPECTED_OUTPUT_KEYS_FIELD_NUMBER: _ClassVar[int]
        ORIGIN_TASK_ID_FIELD_NUMBER: _ClassVar[int]
        PAYLOAD_ID_FIELD_NUMBER: _ClassVar[int]
        RETRY_OF_IDS_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        data_dependencies: _containers.RepeatedScalarFieldContainer[str]
        expected_output_keys: _containers.RepeatedScalarFieldContainer[str]
        origin_task_id: str
        payload_id: str
        retry_of_ids: _containers.RepeatedScalarFieldContainer[str]
        status: _task_status_pb2.TaskStatus
        task_id: str
        def __init__(self, task_id: _Optional[str] = ..., payload_id: _Optional[str] = ..., origin_task_id: _Optional[str] = ..., status: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ..., expected_output_keys: _Optional[_Iterable[str]] = ..., data_dependencies: _Optional[_Iterable[str]] = ..., retry_of_ids: _Optional[_Iterable[str]] = ...) -> None: ...
    class ResultOwnerUpdate(_message.Message):
        __slots__ = ["current_owner_id", "previous_owner_id", "result_id"]
        CURRENT_OWNER_ID_FIELD_NUMBER: _ClassVar[int]
        PREVIOUS_OWNER_ID_FIELD_NUMBER: _ClassVar[int]
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        current_owner_id: str
        previous_owner_id: str
        result_id: str
        def __init__(self, result_id: _Optional[str] = ..., previous_owner_id: _Optional[str] = ..., current_owner_id: _Optional[str] = ...) -> None: ...
    class ResultStatusUpdate(_message.Message):
        __slots__ = ["result_id", "status"]
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        result_id: str
        status: _result_status_pb2.ResultStatus
        def __init__(self, result_id: _Optional[str] = ..., status: _Optional[_Union[_result_status_pb2.ResultStatus, str]] = ...) -> None: ...
    class TaskStatusUpdate(_message.Message):
        __slots__ = ["status", "task_id"]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        status: _task_status_pb2.TaskStatus
        task_id: str
        def __init__(self, task_id: _Optional[str] = ..., status: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ...) -> None: ...
    NEW_RESULT_FIELD_NUMBER: _ClassVar[int]
    NEW_TASK_FIELD_NUMBER: _ClassVar[int]
    RESULT_OWNER_UPDATE_FIELD_NUMBER: _ClassVar[int]
    RESULT_STATUS_UPDATE_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_STATUS_UPDATE_FIELD_NUMBER: _ClassVar[int]
    new_result: EventSubscriptionResponse.NewResult
    new_task: EventSubscriptionResponse.NewTask
    result_owner_update: EventSubscriptionResponse.ResultOwnerUpdate
    result_status_update: EventSubscriptionResponse.ResultStatusUpdate
    session_id: str
    task_status_update: EventSubscriptionResponse.TaskStatusUpdate
    def __init__(self, session_id: _Optional[str] = ..., task_status_update: _Optional[_Union[EventSubscriptionResponse.TaskStatusUpdate, _Mapping]] = ..., result_status_update: _Optional[_Union[EventSubscriptionResponse.ResultStatusUpdate, _Mapping]] = ..., result_owner_update: _Optional[_Union[EventSubscriptionResponse.ResultOwnerUpdate, _Mapping]] = ..., new_task: _Optional[_Union[EventSubscriptionResponse.NewTask, _Mapping]] = ..., new_result: _Optional[_Union[EventSubscriptionResponse.NewResult, _Mapping]] = ...) -> None: ...
