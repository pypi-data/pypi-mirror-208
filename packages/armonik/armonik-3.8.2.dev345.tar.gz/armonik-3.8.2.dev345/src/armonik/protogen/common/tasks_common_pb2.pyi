from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import objects_pb2 as _objects_pb2
from . import task_status_pb2 as _task_status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CancelTasksRequest(_message.Message):
    __slots__ = ["task_ids"]
    TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    task_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, task_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class CancelTasksResponse(_message.Message):
    __slots__ = ["tasks"]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[TaskSummary]
    def __init__(self, tasks: _Optional[_Iterable[_Union[TaskSummary, _Mapping]]] = ...) -> None: ...

class CountTasksByStatusRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class CountTasksByStatusResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _containers.RepeatedCompositeFieldContainer[_objects_pb2.StatusCount]
    def __init__(self, status: _Optional[_Iterable[_Union[_objects_pb2.StatusCount, _Mapping]]] = ...) -> None: ...

class GetResultIdsRequest(_message.Message):
    __slots__ = ["task_id"]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, task_id: _Optional[_Iterable[str]] = ...) -> None: ...

class GetResultIdsResponse(_message.Message):
    __slots__ = ["task_results"]
    class MapTaskResult(_message.Message):
        __slots__ = ["result_ids", "task_id"]
        RESULT_IDS_FIELD_NUMBER: _ClassVar[int]
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        result_ids: _containers.RepeatedScalarFieldContainer[str]
        task_id: str
        def __init__(self, task_id: _Optional[str] = ..., result_ids: _Optional[_Iterable[str]] = ...) -> None: ...
    TASK_RESULTS_FIELD_NUMBER: _ClassVar[int]
    task_results: _containers.RepeatedCompositeFieldContainer[GetResultIdsResponse.MapTaskResult]
    def __init__(self, task_results: _Optional[_Iterable[_Union[GetResultIdsResponse.MapTaskResult, _Mapping]]] = ...) -> None: ...

class GetTaskRequest(_message.Message):
    __slots__ = ["task_id"]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class GetTaskResponse(_message.Message):
    __slots__ = ["task"]
    TASK_FIELD_NUMBER: _ClassVar[int]
    task: TaskRaw
    def __init__(self, task: _Optional[_Union[TaskRaw, _Mapping]] = ...) -> None: ...

class ListTasksRawResponse(_message.Message):
    __slots__ = ["page", "page_size", "tasks", "total"]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    tasks: _containers.RepeatedCompositeFieldContainer[TaskRaw]
    total: int
    def __init__(self, tasks: _Optional[_Iterable[_Union[TaskRaw, _Mapping]]] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class ListTasksRequest(_message.Message):
    __slots__ = ["filter", "page", "page_size", "sort", "with_errors"]
    class OrderByField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class OrderDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class Filter(_message.Message):
        __slots__ = ["created_after", "created_before", "ended_after", "ended_before", "session_id", "started_after", "started_before", "status"]
        CREATED_AFTER_FIELD_NUMBER: _ClassVar[int]
        CREATED_BEFORE_FIELD_NUMBER: _ClassVar[int]
        ENDED_AFTER_FIELD_NUMBER: _ClassVar[int]
        ENDED_BEFORE_FIELD_NUMBER: _ClassVar[int]
        SESSION_ID_FIELD_NUMBER: _ClassVar[int]
        STARTED_AFTER_FIELD_NUMBER: _ClassVar[int]
        STARTED_BEFORE_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        created_after: _timestamp_pb2.Timestamp
        created_before: _timestamp_pb2.Timestamp
        ended_after: _timestamp_pb2.Timestamp
        ended_before: _timestamp_pb2.Timestamp
        session_id: str
        started_after: _timestamp_pb2.Timestamp
        started_before: _timestamp_pb2.Timestamp
        status: _containers.RepeatedScalarFieldContainer[_task_status_pb2.TaskStatus]
        def __init__(self, session_id: _Optional[str] = ..., status: _Optional[_Iterable[_Union[_task_status_pb2.TaskStatus, str]]] = ..., created_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., started_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., started_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ended_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ended_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    class Sort(_message.Message):
        __slots__ = ["direction", "field"]
        DIRECTION_FIELD_NUMBER: _ClassVar[int]
        FIELD_FIELD_NUMBER: _ClassVar[int]
        direction: ListTasksRequest.OrderDirection
        field: ListTasksRequest.OrderByField
        def __init__(self, field: _Optional[_Union[ListTasksRequest.OrderByField, str]] = ..., direction: _Optional[_Union[ListTasksRequest.OrderDirection, str]] = ...) -> None: ...
    FILTER_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_CREATED_AT: ListTasksRequest.OrderByField
    ORDER_BY_FIELD_ENDED_AT: ListTasksRequest.OrderByField
    ORDER_BY_FIELD_SESSION_ID: ListTasksRequest.OrderByField
    ORDER_BY_FIELD_STARTED_AT: ListTasksRequest.OrderByField
    ORDER_BY_FIELD_STATUS: ListTasksRequest.OrderByField
    ORDER_BY_FIELD_TASK_ID: ListTasksRequest.OrderByField
    ORDER_BY_FIELD_UNSPECIFIED: ListTasksRequest.OrderByField
    ORDER_DIRECTION_ASC: ListTasksRequest.OrderDirection
    ORDER_DIRECTION_DESC: ListTasksRequest.OrderDirection
    ORDER_DIRECTION_UNSPECIFIED: ListTasksRequest.OrderDirection
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    WITH_ERRORS_FIELD_NUMBER: _ClassVar[int]
    filter: ListTasksRequest.Filter
    page: int
    page_size: int
    sort: ListTasksRequest.Sort
    with_errors: bool
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., filter: _Optional[_Union[ListTasksRequest.Filter, _Mapping]] = ..., sort: _Optional[_Union[ListTasksRequest.Sort, _Mapping]] = ..., with_errors: bool = ...) -> None: ...

class ListTasksResponse(_message.Message):
    __slots__ = ["page", "page_size", "tasks", "total"]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    tasks: _containers.RepeatedCompositeFieldContainer[TaskSummary]
    total: int
    def __init__(self, tasks: _Optional[_Iterable[_Union[TaskSummary, _Mapping]]] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class SubmitTasksRequest(_message.Message):
    __slots__ = ["session_id", "task_creations", "task_options"]
    class TaskCreation(_message.Message):
        __slots__ = ["data_dependencies", "expected_output_keys", "payload_id", "task_options"]
        DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
        EXPECTED_OUTPUT_KEYS_FIELD_NUMBER: _ClassVar[int]
        PAYLOAD_ID_FIELD_NUMBER: _ClassVar[int]
        TASK_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        data_dependencies: _containers.RepeatedScalarFieldContainer[str]
        expected_output_keys: _containers.RepeatedScalarFieldContainer[str]
        payload_id: str
        task_options: _objects_pb2.TaskOptions
        def __init__(self, expected_output_keys: _Optional[_Iterable[str]] = ..., data_dependencies: _Optional[_Iterable[str]] = ..., payload_id: _Optional[str] = ..., task_options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ...) -> None: ...
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_CREATIONS_FIELD_NUMBER: _ClassVar[int]
    TASK_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    task_creations: _containers.RepeatedCompositeFieldContainer[SubmitTasksRequest.TaskCreation]
    task_options: _objects_pb2.TaskOptions
    def __init__(self, session_id: _Optional[str] = ..., task_options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ..., task_creations: _Optional[_Iterable[_Union[SubmitTasksRequest.TaskCreation, _Mapping]]] = ...) -> None: ...

class SubmitTasksResponse(_message.Message):
    __slots__ = ["task_infos"]
    class TaskInfo(_message.Message):
        __slots__ = ["data_dependencies", "expected_output_ids", "payload_id", "task_id"]
        DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
        EXPECTED_OUTPUT_IDS_FIELD_NUMBER: _ClassVar[int]
        PAYLOAD_ID_FIELD_NUMBER: _ClassVar[int]
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        data_dependencies: _containers.RepeatedScalarFieldContainer[str]
        expected_output_ids: _containers.RepeatedScalarFieldContainer[str]
        payload_id: str
        task_id: str
        def __init__(self, task_id: _Optional[str] = ..., expected_output_ids: _Optional[_Iterable[str]] = ..., data_dependencies: _Optional[_Iterable[str]] = ..., payload_id: _Optional[str] = ...) -> None: ...
    TASK_INFOS_FIELD_NUMBER: _ClassVar[int]
    task_infos: _containers.RepeatedCompositeFieldContainer[SubmitTasksResponse.TaskInfo]
    def __init__(self, task_infos: _Optional[_Iterable[_Union[SubmitTasksResponse.TaskInfo, _Mapping]]] = ...) -> None: ...

class TaskRaw(_message.Message):
    __slots__ = ["acquired_at", "created_at", "creation_to_end_duration", "data_dependencies", "ended_at", "expected_output_ids", "id", "options", "output", "owner_pod_id", "parent_task_ids", "pod_hostname", "pod_ttl", "processing_to_end_duration", "received_at", "retry_of_ids", "session_id", "started_at", "status", "status_message", "submitted_at"]
    class Output(_message.Message):
        __slots__ = ["error", "success"]
        ERROR_FIELD_NUMBER: _ClassVar[int]
        SUCCESS_FIELD_NUMBER: _ClassVar[int]
        error: str
        success: bool
        def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...
    ACQUIRED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATION_TO_END_DURATION_FIELD_NUMBER: _ClassVar[int]
    DATA_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_OUTPUT_IDS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    OWNER_POD_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    POD_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    POD_TTL_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_TO_END_DURATION_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_AT_FIELD_NUMBER: _ClassVar[int]
    RETRY_OF_IDS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUBMITTED_AT_FIELD_NUMBER: _ClassVar[int]
    acquired_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    creation_to_end_duration: _duration_pb2.Duration
    data_dependencies: _containers.RepeatedScalarFieldContainer[str]
    ended_at: _timestamp_pb2.Timestamp
    expected_output_ids: _containers.RepeatedScalarFieldContainer[str]
    id: str
    options: _objects_pb2.TaskOptions
    output: TaskRaw.Output
    owner_pod_id: str
    parent_task_ids: _containers.RepeatedScalarFieldContainer[str]
    pod_hostname: str
    pod_ttl: _timestamp_pb2.Timestamp
    processing_to_end_duration: _duration_pb2.Duration
    received_at: _timestamp_pb2.Timestamp
    retry_of_ids: _containers.RepeatedScalarFieldContainer[str]
    session_id: str
    started_at: _timestamp_pb2.Timestamp
    status: _task_status_pb2.TaskStatus
    status_message: str
    submitted_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., session_id: _Optional[str] = ..., owner_pod_id: _Optional[str] = ..., parent_task_ids: _Optional[_Iterable[str]] = ..., data_dependencies: _Optional[_Iterable[str]] = ..., expected_output_ids: _Optional[_Iterable[str]] = ..., retry_of_ids: _Optional[_Iterable[str]] = ..., status: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ..., status_message: _Optional[str] = ..., options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., submitted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ended_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., creation_to_end_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., processing_to_end_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., pod_ttl: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., output: _Optional[_Union[TaskRaw.Output, _Mapping]] = ..., pod_hostname: _Optional[str] = ..., received_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., acquired_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TaskSummary(_message.Message):
    __slots__ = ["created_at", "creation_to_end_duration", "ended_at", "error", "id", "options", "processing_to_end_duration", "session_id", "started_at", "status"]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATION_TO_END_DURATION_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_TO_END_DURATION_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    created_at: _timestamp_pb2.Timestamp
    creation_to_end_duration: _duration_pb2.Duration
    ended_at: _timestamp_pb2.Timestamp
    error: str
    id: str
    options: _objects_pb2.TaskOptions
    processing_to_end_duration: _duration_pb2.Duration
    session_id: str
    started_at: _timestamp_pb2.Timestamp
    status: _task_status_pb2.TaskStatus
    def __init__(self, id: _Optional[str] = ..., session_id: _Optional[str] = ..., options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ..., status: _Optional[_Union[_task_status_pb2.TaskStatus, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., started_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ended_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., creation_to_end_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., processing_to_end_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...
