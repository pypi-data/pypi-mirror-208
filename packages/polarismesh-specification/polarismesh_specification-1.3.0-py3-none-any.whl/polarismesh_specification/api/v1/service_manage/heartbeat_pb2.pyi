from ..service_manage import service_pb2 as _service_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DelHeartbeatsRequest(_message.Message):
    __slots__ = ["instanceIds"]
    INSTANCEIDS_FIELD_NUMBER: _ClassVar[int]
    instanceIds: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, instanceIds: _Optional[_Iterable[str]] = ...) -> None: ...

class DelHeartbeatsResponse(_message.Message):
    __slots__ = ["code", "info"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    code: int
    info: str
    def __init__(self, code: _Optional[int] = ..., info: _Optional[str] = ...) -> None: ...

class GetHeartbeatsRequest(_message.Message):
    __slots__ = ["instanceIds"]
    INSTANCEIDS_FIELD_NUMBER: _ClassVar[int]
    instanceIds: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, instanceIds: _Optional[_Iterable[str]] = ...) -> None: ...

class GetHeartbeatsResponse(_message.Message):
    __slots__ = ["records"]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    records: _containers.RepeatedCompositeFieldContainer[HeartbeatRecord]
    def __init__(self, records: _Optional[_Iterable[_Union[HeartbeatRecord, _Mapping]]] = ...) -> None: ...

class HeartbeatRecord(_message.Message):
    __slots__ = ["exist", "instanceId", "lastHeartbeatSec"]
    EXIST_FIELD_NUMBER: _ClassVar[int]
    INSTANCEID_FIELD_NUMBER: _ClassVar[int]
    LASTHEARTBEATSEC_FIELD_NUMBER: _ClassVar[int]
    exist: bool
    instanceId: str
    lastHeartbeatSec: int
    def __init__(self, instanceId: _Optional[str] = ..., lastHeartbeatSec: _Optional[int] = ..., exist: bool = ...) -> None: ...

class HeartbeatsRequest(_message.Message):
    __slots__ = ["heartbeats"]
    HEARTBEATS_FIELD_NUMBER: _ClassVar[int]
    heartbeats: _containers.RepeatedCompositeFieldContainer[InstanceHeartbeat]
    def __init__(self, heartbeats: _Optional[_Iterable[_Union[InstanceHeartbeat, _Mapping]]] = ...) -> None: ...

class HeartbeatsResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class InstanceHeartbeat(_message.Message):
    __slots__ = ["host", "instanceId", "namespace", "port", "service"]
    HOST_FIELD_NUMBER: _ClassVar[int]
    INSTANCEID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    host: str
    instanceId: str
    namespace: str
    port: int
    service: str
    def __init__(self, instanceId: _Optional[str] = ..., service: _Optional[str] = ..., namespace: _Optional[str] = ..., host: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...
