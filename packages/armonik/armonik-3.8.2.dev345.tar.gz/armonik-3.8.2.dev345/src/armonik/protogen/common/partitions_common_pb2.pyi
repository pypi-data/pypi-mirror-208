from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetPartitionRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetPartitionResponse(_message.Message):
    __slots__ = ["partition"]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    partition: PartitionRaw
    def __init__(self, partition: _Optional[_Union[PartitionRaw, _Mapping]] = ...) -> None: ...

class ListPartitionsRequest(_message.Message):
    __slots__ = ["filter", "page", "page_size", "sort"]
    class OrderByField(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class OrderDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class Filter(_message.Message):
        __slots__ = ["id", "parent_partition_id", "pod_max", "pod_reserved", "preemption_percentage", "priority"]
        ID_FIELD_NUMBER: _ClassVar[int]
        PARENT_PARTITION_ID_FIELD_NUMBER: _ClassVar[int]
        POD_MAX_FIELD_NUMBER: _ClassVar[int]
        POD_RESERVED_FIELD_NUMBER: _ClassVar[int]
        PREEMPTION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
        PRIORITY_FIELD_NUMBER: _ClassVar[int]
        id: str
        parent_partition_id: str
        pod_max: int
        pod_reserved: int
        preemption_percentage: int
        priority: int
        def __init__(self, id: _Optional[str] = ..., parent_partition_id: _Optional[str] = ..., pod_reserved: _Optional[int] = ..., pod_max: _Optional[int] = ..., preemption_percentage: _Optional[int] = ..., priority: _Optional[int] = ...) -> None: ...
    class Sort(_message.Message):
        __slots__ = ["direction", "field"]
        DIRECTION_FIELD_NUMBER: _ClassVar[int]
        FIELD_FIELD_NUMBER: _ClassVar[int]
        direction: ListPartitionsRequest.OrderDirection
        field: ListPartitionsRequest.OrderByField
        def __init__(self, field: _Optional[_Union[ListPartitionsRequest.OrderByField, str]] = ..., direction: _Optional[_Union[ListPartitionsRequest.OrderDirection, str]] = ...) -> None: ...
    FILTER_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_ID: ListPartitionsRequest.OrderByField
    ORDER_BY_FIELD_PARENT_PARTITION_IDS: ListPartitionsRequest.OrderByField
    ORDER_BY_FIELD_POD_MAX: ListPartitionsRequest.OrderByField
    ORDER_BY_FIELD_POD_RESERVED: ListPartitionsRequest.OrderByField
    ORDER_BY_FIELD_PREEMPTION_PERCENTAGE: ListPartitionsRequest.OrderByField
    ORDER_BY_FIELD_PRIORITY: ListPartitionsRequest.OrderByField
    ORDER_BY_FIELD_UNSPECIFIED: ListPartitionsRequest.OrderByField
    ORDER_DIRECTION_ASC: ListPartitionsRequest.OrderDirection
    ORDER_DIRECTION_DESC: ListPartitionsRequest.OrderDirection
    ORDER_DIRECTION_UNSPECIFIED: ListPartitionsRequest.OrderDirection
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    filter: ListPartitionsRequest.Filter
    page: int
    page_size: int
    sort: ListPartitionsRequest.Sort
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., filter: _Optional[_Union[ListPartitionsRequest.Filter, _Mapping]] = ..., sort: _Optional[_Union[ListPartitionsRequest.Sort, _Mapping]] = ...) -> None: ...

class ListPartitionsResponse(_message.Message):
    __slots__ = ["page", "page_size", "partitions", "total"]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    partitions: _containers.RepeatedCompositeFieldContainer[PartitionRaw]
    total: int
    def __init__(self, partitions: _Optional[_Iterable[_Union[PartitionRaw, _Mapping]]] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class PartitionRaw(_message.Message):
    __slots__ = ["id", "parent_partition_ids", "pod_configuration", "pod_max", "pod_reserved", "preemption_percentage", "priority"]
    class PodConfigurationEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_PARTITION_IDS_FIELD_NUMBER: _ClassVar[int]
    POD_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    POD_MAX_FIELD_NUMBER: _ClassVar[int]
    POD_RESERVED_FIELD_NUMBER: _ClassVar[int]
    PREEMPTION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    parent_partition_ids: _containers.RepeatedScalarFieldContainer[str]
    pod_configuration: _containers.ScalarMap[str, str]
    pod_max: int
    pod_reserved: int
    preemption_percentage: int
    priority: int
    def __init__(self, id: _Optional[str] = ..., parent_partition_ids: _Optional[_Iterable[str]] = ..., pod_reserved: _Optional[int] = ..., pod_max: _Optional[int] = ..., pod_configuration: _Optional[_Mapping[str, str]] = ..., preemption_percentage: _Optional[int] = ..., priority: _Optional[int] = ...) -> None: ...
