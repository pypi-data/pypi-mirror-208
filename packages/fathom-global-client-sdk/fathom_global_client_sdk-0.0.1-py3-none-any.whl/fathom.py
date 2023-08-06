"""The Fathom API client for querying flood and related data."""
import logging
from datetime import timedelta, datetime
from typing import List, Optional

import grpc
from protoc_gen_validate.validator import validate_all

from proto.fathom import fathom_pb2, fathom_pb2_grpc
from proto.geo import geo_pb2

FATHOM_GRPC_CHANNEL_MSG_SIZE = 10 * 1024 * 1024  # default 10MB


class Client:
    """A Client for interacting with the Fathom API."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        api_address: str = "api.fathom.global",
        msg_channel_size: int = FATHOM_GRPC_CHANNEL_MSG_SIZE,
    ) -> None:
        """Constructs a new Client, connected to a remote server.

        Args:
            api_address: Address of the Fathom API server.
            client_id: Client ID to identify a registered client on the
                    authorization server.
            client_secret: Client Secret used with client_id to get an
                    access token.
            msg_channel_size: gRPC message channel size, it is 10MB by
            default but if you will be dealing with data size larger than
            the default, you can configure the size.
        """
        logging.info("fathom.Client: connecting to {}".format(api_address))

        self._api_addr = api_address
        self._client_id = client_id
        self._client_secret = client_secret
        self._auth_conn = None
        self._message_size = msg_channel_size

        # expired at creation.
        self._token_expiry = datetime.utcnow() + timedelta(seconds=-0.5)
        self._stub = self._service_stub()

    def __del__(self) -> None:
        if channel := getattr(self, "_channel", None):
            channel.close()
            logging.info("fathom.Client: closed gRPC channel")

    @property
    def grpc_stub(self) -> fathom_pb2_grpc.FathomServiceStub:
        """Returns the underlying gRPC connection for direct API access.

        See https://grpc.io for more information.
        """
        return self._stub

    def _service_stub(self) -> fathom_pb2_grpc.FathomServiceStub:
        """Checks that the api credentials are still valid using an
        expiration time, creates a new grpc stub or use the previously
        created grpc stub depending on the condition.
        """
        channel_opt = [
            ("grpc.max_send_message_length", self._message_size),
            ("grpc.max_receive_message_length", self._message_size),
        ]

        if self._token_expiry <= datetime.utcnow():
            call_creds = grpc.access_token_call_credentials(self._api_access_token())
            creds = grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(), call_creds
            )
            self._channel = grpc.secure_channel(
                self._api_addr, creds, options=channel_opt
            )
            self._stub = fathom_pb2_grpc.FathomServiceStub(self._channel)

        return self._stub

    def _api_access_token(self) -> str:
        """Returns an access token to authenticate with the Fathom API."""
        try:
            request = fathom_pb2.CreateAccessTokenRequest(
                client_id=self._client_id, client_secret=self._client_secret
            )
            channel = grpc.secure_channel(
                self._api_addr, grpc.ssl_channel_credentials()
            )
            stub = fathom_pb2_grpc.FathomServiceStub(channel)
            response = stub.CreateAccessToken(request)
            channel.close()
            self._token_expiry = datetime.utcnow() + timedelta(
                seconds=response.expire_secs
            )
            return response.access_token
        except Exception as err:
            raise Exception(f"Obtaining access token from auth server: {err}")

    def get_points(
        self, points: geo_pb2.MultiPoint, layer_ids: List[str], project_id: str = None
    ) -> fathom_pb2.GetDataResponse:
        """Returns data pertaining to a list of lat-lng coordinates.

        Args:
            points: A list of points.

            layer_ids: The identifiers of the types of data being requested.

            project_id: string
        """

        request = fathom_pb2.GetDataRequest(
            points=points,
            layers=fathom_pb2.Layers(
                layer_ids=fathom_pb2.Layers.Identifiers(
                    ids=layer_ids,
                ),
            ),
            metadata=_metadata_from_project_id(project_id),
        )

        validate_all(request)

        return self._service_stub().GetData(request)

    def get_polygon(
        self, polygon: geo_pb2.Polygon, layer_ids: List[str], project_id: str = None
    ) -> fathom_pb2.GetDataResponse:
        """Returns data pertaining to a polygon coordinates.

        Args:
            polygon: The bounding points of an area for which data are requested.
            The first and last point MUST be the same, and the loop MUST be in a
            counterclockwise direction (i.e. on the left-hand side of an observer
            walking along the boundary).

            layer_ids: The identifiers of the types of data being requested.

            project_id: string
        """
        request = fathom_pb2.GetDataRequest(
            polygon=polygon,
            layers=fathom_pb2.Layers(
                layer_ids=fathom_pb2.Layers.Identifiers(
                    ids=layer_ids,
                ),
            ),
            metadata=_metadata_from_project_id(project_id),
        )

        validate_all(request)

        return self._service_stub().GetData(request)

    def get_with_shapefile(
        self, file: str, layer_ids: List[str], project_id: str = None
    ) -> fathom_pb2.GetDataResponse:
        """Returns data pertaining to a polygon coordinates from a shapefile.

        Args:
            file: The shapefile containing geometries requested. Only Point,
            MultiPoint, and Polygon are supported.

            layer_ids: The identifiers of the types of data being requested.

            project_id: string
        """
        with open(file, "rb") as f:
            request = fathom_pb2.GetDataRequest(
                shp_file=f.read(),
                layers=fathom_pb2.Layers(
                    layer_ids=fathom_pb2.Layers.Identifiers(
                        ids=layer_ids,
                    ),
                ),
                metadata=_metadata_from_project_id(project_id),
            )

        validate_all(request)

        return self._service_stub().GetData(request)


def _metadata_from_project_id(project_id: Optional[str]) -> Optional[dict]:
    return {"project_id": project_id} if project_id else None


def point(lat: float, lng: float) -> geo_pb2.Point:
    """Returns a Point object for use with Client.get_point()."""
    return geo_pb2.Point(
        latitude=lat,
        longitude=lng,
    )


def points(points: List[geo_pb2.Point]) -> geo_pb2.MultiPoint:
    """Returns a MultiPoint object for use with Client.get_points()."""
    return geo_pb2.MultiPoint(points=points)


def line_string(points: List[geo_pb2.Point]) -> geo_pb2.LineString:
    """Returns a LineString object for use with polygon()."""
    return geo_pb2.LineString(points=points)


def simple_polygon(points: List[geo_pb2.Point]) -> geo_pb2.Polygon:
    """Returns a Polygon object for use with Client.get_polygon()."""
    return geo_pb2.Polygon(
        lines=[
            line_string(points),
        ]
    )


class FathomException(Exception):
    """A client exception"""
