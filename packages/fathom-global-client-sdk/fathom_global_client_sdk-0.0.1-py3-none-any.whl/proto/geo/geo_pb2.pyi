from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class LineString(_message.Message):
    __slots__ = ["points"]
    POINTS_FIELD_NUMBER: ClassVar[int]
    points: _containers.RepeatedCompositeFieldContainer[Point]
    def __init__(self, points: Optional[Iterable[Union[Point, Mapping]]] = ...) -> None: ...

class MultiPoint(_message.Message):
    __slots__ = ["points"]
    POINTS_FIELD_NUMBER: ClassVar[int]
    points: _containers.RepeatedCompositeFieldContainer[Point]
    def __init__(self, points: Optional[Iterable[Union[Point, Mapping]]] = ...) -> None: ...

class Point(_message.Message):
    __slots__ = ["latitude", "longitude"]
    LATITUDE_FIELD_NUMBER: ClassVar[int]
    LONGITUDE_FIELD_NUMBER: ClassVar[int]
    latitude: float
    longitude: float
    def __init__(self, longitude: Optional[float] = ..., latitude: Optional[float] = ...) -> None: ...

class Polygon(_message.Message):
    __slots__ = ["lines"]
    LINES_FIELD_NUMBER: ClassVar[int]
    lines: _containers.RepeatedCompositeFieldContainer[LineString]
    def __init__(self, lines: Optional[Iterable[Union[LineString, Mapping]]] = ...) -> None: ...
