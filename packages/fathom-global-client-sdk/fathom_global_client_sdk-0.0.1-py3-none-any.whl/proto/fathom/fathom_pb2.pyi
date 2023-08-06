from google.api import annotations_pb2 as _annotations_pb2
from proto.data import data_pb2 as _data_pb2
from proto.geo import geo_pb2 as _geo_pb2
from proto.portfolio import portfolio_pb2 as _portfolio_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Text, Union

DESCRIPTOR: _descriptor.FileDescriptor
NO_DATA: Code
PERMANENT_WATER: Code
UNSPECIFIED: Code

class CreateAccessTokenRequest(_message.Message):
    __slots__ = ["client_id", "client_secret"]
    CLIENT_ID_FIELD_NUMBER: ClassVar[int]
    CLIENT_SECRET_FIELD_NUMBER: ClassVar[int]
    client_id: str
    client_secret: str
    def __init__(self, client_id: Optional[str] = ..., client_secret: Optional[str] = ...) -> None: ...

class CreateAccessTokenResponse(_message.Message):
    __slots__ = ["access_token", "expire_secs"]
    ACCESS_TOKEN_FIELD_NUMBER: ClassVar[int]
    EXPIRE_SECS_FIELD_NUMBER: ClassVar[int]
    access_token: str
    expire_secs: int
    def __init__(self, access_token: Optional[str] = ..., expire_secs: Optional[int] = ...) -> None: ...

class Data(_message.Message):
    __slots__ = ["code", "polygons", "resolution", "values"]
    class Value(_message.Message):
        __slots__ = ["code", "query_point", "sw_corner", "val"]
        CODE_FIELD_NUMBER: ClassVar[int]
        QUERY_POINT_FIELD_NUMBER: ClassVar[int]
        SW_CORNER_FIELD_NUMBER: ClassVar[int]
        VAL_FIELD_NUMBER: ClassVar[int]
        code: Code
        query_point: _geo_pb2.Point
        sw_corner: _geo_pb2.Point
        val: int
        def __init__(self, sw_corner: Optional[Union[_geo_pb2.Point, Mapping]] = ..., query_point: Optional[Union[_geo_pb2.Point, Mapping]] = ..., val: Optional[int] = ..., code: Optional[Union[Code, str]] = ...) -> None: ...
    CODE_FIELD_NUMBER: ClassVar[int]
    POLYGONS_FIELD_NUMBER: ClassVar[int]
    RESOLUTION_FIELD_NUMBER: ClassVar[int]
    VALUES_FIELD_NUMBER: ClassVar[int]
    code: Code
    polygons: Polygons
    resolution: _data_pb2.Resolution
    values: _containers.RepeatedCompositeFieldContainer[Data.Value]
    def __init__(self, resolution: Optional[Union[_data_pb2.Resolution, str]] = ..., values: Optional[Iterable[Union[Data.Value, Mapping]]] = ..., polygons: Optional[Union[Polygons, Mapping]] = ..., code: Optional[Union[Code, str]] = ...) -> None: ...

class GetDataRequest(_message.Message):
    __slots__ = ["layers", "metadata", "points", "polygon", "shp_file"]
    class MetadataEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: str
        def __init__(self, key: Optional[str] = ..., value: Optional[str] = ...) -> None: ...
    LAYERS_FIELD_NUMBER: ClassVar[int]
    METADATA_FIELD_NUMBER: ClassVar[int]
    POINTS_FIELD_NUMBER: ClassVar[int]
    POLYGON_FIELD_NUMBER: ClassVar[int]
    SHP_FILE_FIELD_NUMBER: ClassVar[int]
    layers: Layers
    metadata: _containers.ScalarMap[str, str]
    points: _geo_pb2.MultiPoint
    polygon: _geo_pb2.Polygon
    shp_file: bytes
    def __init__(self, polygon: Optional[Union[_geo_pb2.Polygon, Mapping]] = ..., points: Optional[Union[_geo_pb2.MultiPoint, Mapping]] = ..., shp_file: Optional[bytes] = ..., layers: Optional[Union[Layers, Mapping]] = ..., metadata: Optional[Mapping[str, str]] = ...) -> None: ...

class GetDataResponse(_message.Message):
    __slots__ = ["results"]
    class ResultsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: Data
        def __init__(self, key: Optional[str] = ..., value: Optional[Union[Data, Mapping]] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: ClassVar[int]
    results: _containers.MessageMap[str, Data]
    def __init__(self, results: Optional[Mapping[str, Data]] = ...) -> None: ...

class Layers(_message.Message):
    __slots__ = ["layer_ids"]
    class Identifiers(_message.Message):
        __slots__ = ["ids"]
        IDS_FIELD_NUMBER: ClassVar[int]
        ids: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, ids: Optional[Iterable[str]] = ...) -> None: ...
    LAYER_IDS_FIELD_NUMBER: ClassVar[int]
    layer_ids: Layers.Identifiers
    def __init__(self, layer_ids: Optional[Union[Layers.Identifiers, Mapping]] = ...) -> None: ...

class ListAvailableDataRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ListAvailableDataResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Polygons(_message.Message):
    __slots__ = ["geo_tiffs"]
    GEO_TIFFS_FIELD_NUMBER: ClassVar[int]
    geo_tiffs: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, geo_tiffs: Optional[Iterable[bytes]] = ...) -> None: ...

class Code(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
