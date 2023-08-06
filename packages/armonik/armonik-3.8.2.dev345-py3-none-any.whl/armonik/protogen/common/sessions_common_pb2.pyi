from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import objects_pb2 as _objects_pb2
from . import session_status_pb2 as _session_status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CancelSessionRequest(_message.Message):
    __slots__ = ["session_id"]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class CancelSessionResponse(_message.Message):
    __slots__ = ["session"]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: SessionRaw
    def __init__(self, session: _Optional[_Union[SessionRaw, _Mapping]] = ...) -> None: ...

class CountTasksByStatusRequest(_message.Message):
    __slots__ = ["session_id"]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class CountTasksByStatusResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _containers.RepeatedCompositeFieldContainer[_objects_pb2.StatusCount]
    def __init__(self, status: _Optional[_Iterable[_Union[_objects_pb2.StatusCount, _Mapping]]] = ...) -> None: ...

class GetSessionRequest(_message.Message):
    __slots__ = ["session_id"]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class GetSessionResponse(_message.Message):
    __slots__ = ["session"]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: SessionRaw
    def __init__(self, session: _Optional[_Union[SessionRaw, _Mapping]] = ...) -> None: ...

class ListSessionsRequest(_message.Message):
    __slots__ = ["filter", "page", "page_size", "sort", "with_task_options"]
    class OrderByField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class OrderDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class Filter(_message.Message):
        __slots__ = ["application_name", "application_version", "cancelled_after", "cancelled_before", "created_after", "created_before", "session_id", "status"]
        APPLICATION_NAME_FIELD_NUMBER: _ClassVar[int]
        APPLICATION_VERSION_FIELD_NUMBER: _ClassVar[int]
        CANCELLED_AFTER_FIELD_NUMBER: _ClassVar[int]
        CANCELLED_BEFORE_FIELD_NUMBER: _ClassVar[int]
        CREATED_AFTER_FIELD_NUMBER: _ClassVar[int]
        CREATED_BEFORE_FIELD_NUMBER: _ClassVar[int]
        SESSION_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        application_name: str
        application_version: str
        cancelled_after: _timestamp_pb2.Timestamp
        cancelled_before: _timestamp_pb2.Timestamp
        created_after: _timestamp_pb2.Timestamp
        created_before: _timestamp_pb2.Timestamp
        session_id: str
        status: _session_status_pb2.SessionStatus
        def __init__(self, application_name: _Optional[str] = ..., application_version: _Optional[str] = ..., session_id: _Optional[str] = ..., created_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cancelled_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cancelled_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[_Union[_session_status_pb2.SessionStatus, str]] = ...) -> None: ...
    class Sort(_message.Message):
        __slots__ = ["direction", "field"]
        DIRECTION_FIELD_NUMBER: _ClassVar[int]
        FIELD_FIELD_NUMBER: _ClassVar[int]
        direction: ListSessionsRequest.OrderDirection
        field: ListSessionsRequest.OrderByField
        def __init__(self, field: _Optional[_Union[ListSessionsRequest.OrderByField, str]] = ..., direction: _Optional[_Union[ListSessionsRequest.OrderDirection, str]] = ...) -> None: ...
    FILTER_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_CANCELLED_AT: ListSessionsRequest.OrderByField
    ORDER_BY_FIELD_CREATED_AT: ListSessionsRequest.OrderByField
    ORDER_BY_FIELD_SESSION_ID: ListSessionsRequest.OrderByField
    ORDER_BY_FIELD_STATUS: ListSessionsRequest.OrderByField
    ORDER_BY_FIELD_UNSPECIFIED: ListSessionsRequest.OrderByField
    ORDER_DIRECTION_ASC: ListSessionsRequest.OrderDirection
    ORDER_DIRECTION_DESC: ListSessionsRequest.OrderDirection
    ORDER_DIRECTION_UNSPECIFIED: ListSessionsRequest.OrderDirection
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    WITH_TASK_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    filter: ListSessionsRequest.Filter
    page: int
    page_size: int
    sort: ListSessionsRequest.Sort
    with_task_options: bool
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., filter: _Optional[_Union[ListSessionsRequest.Filter, _Mapping]] = ..., sort: _Optional[_Union[ListSessionsRequest.Sort, _Mapping]] = ..., with_task_options: bool = ...) -> None: ...

class ListSessionsResponse(_message.Message):
    __slots__ = ["page", "page_size", "sessions", "total"]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    sessions: _containers.RepeatedCompositeFieldContainer[SessionSummary]
    total: int
    def __init__(self, sessions: _Optional[_Iterable[_Union[SessionSummary, _Mapping]]] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class SessionRaw(_message.Message):
    __slots__ = ["cancelled_at", "created_at", "duration", "options", "partition_ids", "session_id", "status"]
    CANCELLED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    PARTITION_IDS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    cancelled_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    duration: _duration_pb2.Duration
    options: _objects_pb2.TaskOptions
    partition_ids: _containers.RepeatedScalarFieldContainer[str]
    session_id: str
    status: _session_status_pb2.SessionStatus
    def __init__(self, session_id: _Optional[str] = ..., status: _Optional[_Union[_session_status_pb2.SessionStatus, str]] = ..., partition_ids: _Optional[_Iterable[str]] = ..., options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cancelled_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class SessionSummary(_message.Message):
    __slots__ = ["cancelled_at", "created_at", "duration", "options", "session_id", "status"]
    CANCELLED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    cancelled_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    duration: _duration_pb2.Duration
    options: _objects_pb2.TaskOptions
    session_id: str
    status: _session_status_pb2.SessionStatus
    def __init__(self, session_id: _Optional[str] = ..., status: _Optional[_Union[_session_status_pb2.SessionStatus, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cancelled_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., options: _Optional[_Union[_objects_pb2.TaskOptions, _Mapping]] = ...) -> None: ...
