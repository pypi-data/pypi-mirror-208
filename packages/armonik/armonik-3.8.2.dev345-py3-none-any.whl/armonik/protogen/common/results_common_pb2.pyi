from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import result_status_pb2 as _result_status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateResultsMetaDataRequest(_message.Message):
    __slots__ = ["results", "session_id"]
    class ResultCreate(_message.Message):
        __slots__ = ["name"]
        NAME_FIELD_NUMBER: _ClassVar[int]
        name: str
        def __init__(self, name: _Optional[str] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[CreateResultsMetaDataRequest.ResultCreate]
    session_id: str
    def __init__(self, results: _Optional[_Iterable[_Union[CreateResultsMetaDataRequest.ResultCreate, _Mapping]]] = ..., session_id: _Optional[str] = ...) -> None: ...

class CreateResultsMetaDataResponse(_message.Message):
    __slots__ = ["results"]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ResultRaw]
    def __init__(self, results: _Optional[_Iterable[_Union[ResultRaw, _Mapping]]] = ...) -> None: ...

class CreateResultsRequest(_message.Message):
    __slots__ = ["results", "session_id"]
    class ResultCreate(_message.Message):
        __slots__ = ["data", "name"]
        DATA_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        data: bytes
        name: str
        def __init__(self, name: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[CreateResultsRequest.ResultCreate]
    session_id: str
    def __init__(self, results: _Optional[_Iterable[_Union[CreateResultsRequest.ResultCreate, _Mapping]]] = ..., session_id: _Optional[str] = ...) -> None: ...

class CreateResultsResponse(_message.Message):
    __slots__ = ["results"]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ResultRaw]
    def __init__(self, results: _Optional[_Iterable[_Union[ResultRaw, _Mapping]]] = ...) -> None: ...

class DeleteResultsDataRequest(_message.Message):
    __slots__ = ["result_id", "session_id"]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    result_id: _containers.RepeatedScalarFieldContainer[str]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ..., result_id: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteResultsDataResponse(_message.Message):
    __slots__ = ["result_id", "session_id"]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    result_id: _containers.RepeatedScalarFieldContainer[str]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ..., result_id: _Optional[_Iterable[str]] = ...) -> None: ...

class DownloadResultDataRequest(_message.Message):
    __slots__ = ["result_id", "session_id"]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    result_id: str
    session_id: str
    def __init__(self, session_id: _Optional[str] = ..., result_id: _Optional[str] = ...) -> None: ...

class DownloadResultDataResponse(_message.Message):
    __slots__ = ["data_chunk"]
    DATA_CHUNK_FIELD_NUMBER: _ClassVar[int]
    data_chunk: bytes
    def __init__(self, data_chunk: _Optional[bytes] = ...) -> None: ...

class GetOwnerTaskIdRequest(_message.Message):
    __slots__ = ["result_id", "session_id"]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    result_id: _containers.RepeatedScalarFieldContainer[str]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ..., result_id: _Optional[_Iterable[str]] = ...) -> None: ...

class GetOwnerTaskIdResponse(_message.Message):
    __slots__ = ["result_task", "session_id"]
    class MapResultTask(_message.Message):
        __slots__ = ["result_id", "task_id"]
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        TASK_ID_FIELD_NUMBER: _ClassVar[int]
        result_id: str
        task_id: str
        def __init__(self, result_id: _Optional[str] = ..., task_id: _Optional[str] = ...) -> None: ...
    RESULT_TASK_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    result_task: _containers.RepeatedCompositeFieldContainer[GetOwnerTaskIdResponse.MapResultTask]
    session_id: str
    def __init__(self, result_task: _Optional[_Iterable[_Union[GetOwnerTaskIdResponse.MapResultTask, _Mapping]]] = ..., session_id: _Optional[str] = ...) -> None: ...

class ListResultsRequest(_message.Message):
    __slots__ = ["filter", "page", "page_size", "sort"]
    class OrderByField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class OrderDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class Filter(_message.Message):
        __slots__ = ["completed_after", "completed_before", "created_after", "created_before", "name", "owner_task_id", "result_id", "session_id", "status", "wait_for_data_after", "wait_for_data_before"]
        COMPLETED_AFTER_FIELD_NUMBER: _ClassVar[int]
        COMPLETED_BEFORE_FIELD_NUMBER: _ClassVar[int]
        CREATED_AFTER_FIELD_NUMBER: _ClassVar[int]
        CREATED_BEFORE_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        OWNER_TASK_ID_FIELD_NUMBER: _ClassVar[int]
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        SESSION_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        WAIT_FOR_DATA_AFTER_FIELD_NUMBER: _ClassVar[int]
        WAIT_FOR_DATA_BEFORE_FIELD_NUMBER: _ClassVar[int]
        completed_after: _timestamp_pb2.Timestamp
        completed_before: _timestamp_pb2.Timestamp
        created_after: _timestamp_pb2.Timestamp
        created_before: _timestamp_pb2.Timestamp
        name: str
        owner_task_id: str
        result_id: str
        session_id: str
        status: _result_status_pb2.ResultStatus
        wait_for_data_after: _timestamp_pb2.Timestamp
        wait_for_data_before: _timestamp_pb2.Timestamp
        def __init__(self, session_id: _Optional[str] = ..., name: _Optional[str] = ..., owner_task_id: _Optional[str] = ..., status: _Optional[_Union[_result_status_pb2.ResultStatus, str]] = ..., created_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., completed_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., completed_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., wait_for_data_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., wait_for_data_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., result_id: _Optional[str] = ...) -> None: ...
    class Sort(_message.Message):
        __slots__ = ["direction", "field"]
        DIRECTION_FIELD_NUMBER: _ClassVar[int]
        FIELD_FIELD_NUMBER: _ClassVar[int]
        direction: ListResultsRequest.OrderDirection
        field: ListResultsRequest.OrderByField
        def __init__(self, field: _Optional[_Union[ListResultsRequest.OrderByField, str]] = ..., direction: _Optional[_Union[ListResultsRequest.OrderDirection, str]] = ...) -> None: ...
    FILTER_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_CREATED_AT: ListResultsRequest.OrderByField
    ORDER_BY_FIELD_NAME: ListResultsRequest.OrderByField
    ORDER_BY_FIELD_OWNER_TASK_ID: ListResultsRequest.OrderByField
    ORDER_BY_FIELD_RESULT_ID: ListResultsRequest.OrderByField
    ORDER_BY_FIELD_SESSION_ID: ListResultsRequest.OrderByField
    ORDER_BY_FIELD_STATUS: ListResultsRequest.OrderByField
    ORDER_BY_FIELD_UNSPECIFIED: ListResultsRequest.OrderByField
    ORDER_DIRECTION_ASC: ListResultsRequest.OrderDirection
    ORDER_DIRECTION_DESC: ListResultsRequest.OrderDirection
    ORDER_DIRECTION_UNSPECIFIED: ListResultsRequest.OrderDirection
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    filter: ListResultsRequest.Filter
    page: int
    page_size: int
    sort: ListResultsRequest.Sort
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., filter: _Optional[_Union[ListResultsRequest.Filter, _Mapping]] = ..., sort: _Optional[_Union[ListResultsRequest.Sort, _Mapping]] = ...) -> None: ...

class ListResultsResponse(_message.Message):
    __slots__ = ["page", "page_size", "results", "total"]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    results: _containers.RepeatedCompositeFieldContainer[ResultRaw]
    total: int
    def __init__(self, results: _Optional[_Iterable[_Union[ResultRaw, _Mapping]]] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class ResultRaw(_message.Message):
    __slots__ = ["completed_at", "created_at", "name", "owner_task_id", "result_id", "session_id", "status", "wait_for_data_at"]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    WAIT_FOR_DATA_AT_FIELD_NUMBER: _ClassVar[int]
    completed_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    name: str
    owner_task_id: str
    result_id: str
    session_id: str
    status: _result_status_pb2.ResultStatus
    wait_for_data_at: _timestamp_pb2.Timestamp
    def __init__(self, session_id: _Optional[str] = ..., name: _Optional[str] = ..., owner_task_id: _Optional[str] = ..., status: _Optional[_Union[_result_status_pb2.ResultStatus, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., completed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., wait_for_data_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., result_id: _Optional[str] = ...) -> None: ...

class ResultsServiceConfigurationResponse(_message.Message):
    __slots__ = ["data_chunk_max_size"]
    DATA_CHUNK_MAX_SIZE_FIELD_NUMBER: _ClassVar[int]
    data_chunk_max_size: int
    def __init__(self, data_chunk_max_size: _Optional[int] = ...) -> None: ...

class UploadResultDataRequest(_message.Message):
    __slots__ = ["data_chunk", "id"]
    class ResultIdentifier(_message.Message):
        __slots__ = ["result_id", "session_id"]
        RESULT_ID_FIELD_NUMBER: _ClassVar[int]
        SESSION_ID_FIELD_NUMBER: _ClassVar[int]
        result_id: str
        session_id: str
        def __init__(self, session_id: _Optional[str] = ..., result_id: _Optional[str] = ...) -> None: ...
    DATA_CHUNK_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    data_chunk: bytes
    id: UploadResultDataRequest.ResultIdentifier
    def __init__(self, id: _Optional[_Union[UploadResultDataRequest.ResultIdentifier, _Mapping]] = ..., data_chunk: _Optional[bytes] = ...) -> None: ...

class UploadResultDataResponse(_message.Message):
    __slots__ = ["result"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: ResultRaw
    def __init__(self, result: _Optional[_Union[ResultRaw, _Mapping]] = ...) -> None: ...
