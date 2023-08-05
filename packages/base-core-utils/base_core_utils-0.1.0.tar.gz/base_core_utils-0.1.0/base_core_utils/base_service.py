import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Any, List

# from google.protobuf.struct_pb2 import Value
from google.protobuf.wrappers_pb2 import BoolValue
from grpclib.client import Channel
from grpclib.server import Server

from logger import log

grpc_gen_path = Path(__file__).resolve().parent.parent.parent / "grpc_gen"
sys.path.insert(0, str(grpc_gen_path))

# from grpc_gen.helper_pb2 import Filter


class BaseService:
    @property
    def _client_host(self) -> str | None:
        return self.__client_host

    @_client_host.setter
    def _client_host(self, value) -> None:
        self.__client_host = value

    @property
    def _client_port(self) -> int | None:
        return self.__client_port

    @_client_port.setter
    def _client_port(self, value) -> None:
        self.__client_port = value

    @property
    def _server_host(self) -> str | None:
        return self.__server_host

    @_server_host.setter
    def _server_host(self, value) -> None:
        self.__server_host = value

    @property
    def _server_port(self) -> int | None:
        return self.__server_port

    @_server_port.setter
    def _server_port(self, value) -> None:
        self.__server_port = value

    def _get_class_name(self):
        return type(self).__name__

    @asynccontextmanager
    async def get_service_channel(self) -> AsyncGenerator[Channel, None]:
        async with Channel(self._client_host, self._client_port) as channel:
            yield channel

    async def start_grpc_server(self):
        server = Server([self])
        await server.start(self._server_host, self._server_port)
        log.info(f"{self._get_class_name()} gRPC server is running on {self._server_host}:{self._server_port}")
        await server.wait_closed()

    @staticmethod
    def obj_db_to_protobuf(obj_db: Any, obj_proto: Any, fields: list = None) -> Any:
        if fields is None or not fields:
            fields = set(field.name for field in obj_proto.DESCRIPTOR.fields)

        for field_name in fields:
            if hasattr(obj_db, field_name):
                value = getattr(obj_db, field_name)
                if value is not None:
                    if isinstance(value, bool):
                        bool_value = BoolValue(value=value)
                        getattr(obj_proto, field_name).CopyFrom(bool_value)
                    else:
                        setattr(obj_proto, field_name, value)
        return obj_proto

    # @staticmethod
    # def filters_to_proto(filters: dict[str, Any]) -> List[Filter]:
    #     proto_filters = []
    #     for key, value in filters.items():
    #         filter_value = Value()
    #         if isinstance(value, str):
    #             filter_value.string_value = value
    #         elif isinstance(value, (int, float)):
    #             filter_value.number_value = value
    #         elif isinstance(value, bool):
    #             filter_value.bool_value = value
    #         else:
    #             raise ValueError(f"Unsupported value type: {type(value)}")
    #         proto_filters.append(Filter(field=key, value=filter_value))
    #     return proto_filters
    #
    # @staticmethod
    # def filters_from_proto(proto_filters: List[Filter]) -> dict[str, Any]:
    #     filters = {}
    #     for proto_filter in proto_filters:
    #         value = proto_filter.value
    #         if value.HasField("string_value"):
    #             filters[proto_filter.field] = value.string_value
    #         elif value.HasField("number_value"):
    #             filters[proto_filter.field] = value.number_value
    #         elif value.HasField("bool_value"):
    #             filters[proto_filter.field] = value.bool_value
    #         else:
    #             raise ValueError(f"Unsupported value type in filter: {proto_filter.field}")
    #     return filters
