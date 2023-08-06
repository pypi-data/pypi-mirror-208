from google.api import annotations_pb2 as _annotations_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Optional, Text

DESCRIPTOR: _descriptor.FileDescriptor

class CreatePortfolioTaskRequest(_message.Message):
    __slots__ = ["layer_ids"]
    LAYER_IDS_FIELD_NUMBER: ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, layer_ids: Optional[Iterable[str]] = ...) -> None: ...

class CreatePortfolioTaskResponse(_message.Message):
    __slots__ = ["task_id", "upload_url"]
    TASK_ID_FIELD_NUMBER: ClassVar[int]
    UPLOAD_URL_FIELD_NUMBER: ClassVar[int]
    task_id: str
    upload_url: str
    def __init__(self, task_id: Optional[str] = ..., upload_url: Optional[str] = ...) -> None: ...

class PortfolioStatusRequest(_message.Message):
    __slots__ = ["task_id"]
    TASK_ID_FIELD_NUMBER: ClassVar[int]
    task_id: str
    def __init__(self, task_id: Optional[str] = ...) -> None: ...

class PortfolioStatusResponse(_message.Message):
    __slots__ = ["download_url", "errors", "task_status"]
    DOWNLOAD_URL_FIELD_NUMBER: ClassVar[int]
    ERRORS_FIELD_NUMBER: ClassVar[int]
    TASK_STATUS_FIELD_NUMBER: ClassVar[int]
    download_url: str
    errors: _containers.RepeatedScalarFieldContainer[str]
    task_status: str
    def __init__(self, task_status: Optional[str] = ..., download_url: Optional[str] = ..., errors: Optional[Iterable[str]] = ...) -> None: ...
