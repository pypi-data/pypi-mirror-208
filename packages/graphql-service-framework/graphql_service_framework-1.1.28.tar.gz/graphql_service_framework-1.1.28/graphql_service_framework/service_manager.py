import asyncio
import enum
import os
import datetime
import logging

from dataclasses import dataclass
from typing import List, Any, Optional, Type
from packaging import version as packaging_version, specifiers

from graphql_api import GraphQLAPI, field
from graphql_api.remote import GraphQLRemoteObject, GraphQLRemoteExecutor
from graphql_api.utils import to_camel_case

from graphql_http_server import GraphQLHTTPServer


class ServiceConnectionState(enum.Enum):
    UNKNOWN = "UNKNOWN"
    CONFIG_ERROR = "CONFIG_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    OK = "OK"


@dataclass
class ServiceConnection:
    name: str
    schema_version_specifier: Optional[str] = None
    service_url: Optional[str] = None
    service_manager_url: Optional[str] = None
    http_method: str = "POST"
    raise_error: bool = True
    ignore_service_manager_error: bool = True
    schema: Type = None
    state: ServiceConnectionState = ServiceConnectionState.UNKNOWN

    remote_name: Optional[str] = None
    remote_schema_version: Optional[str] = None
    remote_service_version: Optional[str] = None
    remote_service_manager: "ServiceManager" = None
    remote_service: GraphQLRemoteObject = None

    @classmethod
    def graphql_exclude_fields(cls) -> List[str]:
        return [
            "schema",
            "remote_service",
            "remote_service_manager",
        ]

    def __post_init__(self):
        if self.schema:
            if hasattr(self.schema, "api_version"):
                try:
                    schema_version = getattr(self.schema, "schema_version")
                    schema_version = packaging_version.Version(schema_version)
                    if not self.schema_version_specifier:
                        self.schema_version_specifier = (
                            f"~={schema_version.major}" f".{schema_version.minor}"
                        )
                except Exception:
                    logging.warning(
                        f"Could not identify the schema_version for the "
                        f"connection to {self.name} at {self.service_url}"
                    )

        if self.service_url and self.schema:
            self.remote_service = GraphQLRemoteObject(
                executor=GraphQLRemoteExecutor(
                    name=to_camel_case(self.name, title=True),
                    url=self.service_url,
                    http_method=self.http_method,
                ),
                api=GraphQLAPI(root=self.schema),
            )

    async def async_connect(
        self, connection_logs: List = None, timeout: int = 5
    ) -> bool:
        if connection_logs is None:
            connection_logs = []

        if not self.service_url:
            self.state = ServiceConnectionState.CONFIG_ERROR
            connection_logs.append(
                f"[{datetime.datetime.utcnow()}] ERROR: Missing URL"
                f" for service {self.name}"
            )

            if self.raise_error:
                raise TypeError(f"Missing URL for service {self.name}")
            return False

        if not self.schema:
            self.state = ServiceConnectionState.CONFIG_ERROR
            connection_logs.append(
                f"[{datetime.datetime.utcnow()}] ERROR: Missing schema"
                f" for service {self.name}"
            )

            if self.raise_error:
                raise TypeError(f"Missing schema for service {self.name}")
            return False

        name = to_camel_case(self.name, title=True) + "Service"

        connection_logs.append(
            f"[{datetime.datetime.utcnow()}] "
            f"connecting to {name} {self.service_url}"
        )

        if self.service_manager_url:
            # Attempt to connect to a Service Directory
            connection_logs.append(
                f"[{datetime.datetime.utcnow()}] connecting to Service "
                f"Manager for {name} {self.service_manager_url}"
            )

            # noinspection PyTypeChecker
            self.remote_service_manager: ServiceManager = GraphQLRemoteObject(
                executor=GraphQLRemoteExecutor(
                    name=name,
                    url=self.service_manager_url,
                    http_method=self.http_method,
                    http_timeout=timeout,
                ),
                api=GraphQLAPI(root=ServiceManager),
            )

            a = datetime.datetime.now()
            service_manager_error = False
            uptime = None
            try:
                uptime = await self.remote_service_manager.call_async("uptime")
            except Exception as err:
                msg = "" if self.ignore_service_manager_error else "ERROR: "
                connection_logs.append(
                    f"[{datetime.datetime.utcnow()}] {msg}unable to connect "
                    f"to {name} service manager, timed out after "
                    f"{timeout} seconds. {err}"
                )
                self.state = ServiceConnectionState.CONNECTION_ERROR
                if self.ignore_service_manager_error:
                    service_manager_error = True

                elif self.raise_error:
                    raise ConnectionError(
                        f"unable to connect to {name}, timed out after "
                        f"{timeout} seconds, error {err}"
                    )
                else:
                    return False

            if not service_manager_error:
                b = datetime.datetime.now()

                self.remote_name = await self.remote_service_manager.call_async("name")
                self.remote_schema_version = (
                    await self.remote_service_manager.call_async("schema_version")
                )
                self.remote_service_version = (
                    await self.remote_service_manager.call_async("service_version")
                )

                delta = b - a
                connection_logs.append(
                    f"[{datetime.datetime.utcnow()}] {name} "
                    f"Response time {delta} Uptime {uptime}"
                )

                if self.schema_version_specifier:
                    try:
                        specifier = specifiers.SpecifierSet(
                            self.schema_version_specifier, prereleases=True
                        )
                    except specifiers.InvalidSpecifier as err:
                        connection_logs.append(
                            f"[{datetime.datetime.utcnow()}] "
                            f"ERROR: {name} malformed schema version specifier "
                            f"{self.schema_version_specifier}"
                        )
                        self.state = ServiceConnectionState.VALIDATION_ERROR
                        if self.raise_error:
                            raise err
                        return False

                    try:
                        remote_schema_version = packaging_version.Version(
                            self.remote_schema_version.replace(".dev", "")
                        )
                    except packaging_version.InvalidVersion as err:
                        connection_logs.append(
                            f"[{datetime.datetime.utcnow()}] "
                            f"ERROR: {name} malformed schema version found "
                            f"{self.schema_version_specifier}"
                        )
                        self.state = ServiceConnectionState.VALIDATION_ERROR
                        if self.raise_error:
                            raise err
                        return False

                    if not specifier.contains(remote_schema_version, prereleases=True):
                        connection_logs.append(
                            f"[{datetime.datetime.utcnow()}] ERROR: "
                            f"{name} schema_version mismatch, found "
                            f"{self.remote_schema_version}, required "
                            f"{self.schema_version_specifier}"
                        )
                        self.state = ServiceConnectionState.VALIDATION_ERROR
                        if self.raise_error:
                            raise TypeError(
                                f"[{datetime.datetime.utcnow()}] {name} "
                                f"schema_version mismatch at {self.service_url}, "
                                f"expecting version "
                                f"{self.schema_version_specifier} "
                                f"but {self.service_url} identified as "
                                f"{self.remote_name} version "
                                f"{self.remote_schema_version}."
                            )
                        return False
                    else:
                        connection_logs.append(
                            f"[{datetime.datetime.utcnow()}] {name} schema "
                            f"version match {self.remote_schema_version} is valid"
                            f" for {self.schema_version_specifier}"
                        )

        executor = GraphQLRemoteExecutor(
            name=name,
            url=self.service_url,
            http_method=self.http_method,
            http_timeout=timeout,
        )
        response = None

        try:
            response = await executor.execute_async("query { __typename }")
        except Exception as err:
            connection_logs.append(
                f"[{datetime.datetime.utcnow()}] ERROR: {name} API error "
                f"from {self.service_url}. {err}"
            )
            self.state = ServiceConnectionState.CONNECTION_ERROR
            if self.raise_error:
                raise err
            return False
        else:
            if response.errors:
                connection_logs.append(
                    f"[{datetime.datetime.utcnow()}] ERROR: {name} API "
                    f"Response error from {self.service_url}. "
                    f"{response}"
                )
                self.state = ServiceConnectionState.CONNECTION_ERROR
                if self.raise_error:
                    raise ConnectionError(
                        f"[{datetime.datetime.utcnow()}] ERROR: {name} API "
                        f"Response error from {self.service_url}. "
                        f"{response}"
                    )
                return False

        self.state = ServiceConnectionState.OK
        connection_logs.append(
            f"[{datetime.datetime.utcnow()}] ServiceState = OK "
            f"for {name} {self.service_url}"
        )
        return True


class ServiceManager:
    """
    A manager for a service that advertises the status of the service and
    creates and maintains connections to other services.
    """

    def __init__(
        self,
        name: str,
        schema: Any = None,
        schema_version: str = None,
        service_version: str = None,
        connections: List[ServiceConnection] = None,
        connect_on_init: bool = True,
        connect_timeout: int = 5,
    ):
        if not connections:
            connections = []

        self._connections = connections
        self.connect_on_init = connect_on_init
        self.connect_timeout = connect_timeout

        if schema is not None:
            if schema_version is not None:
                raise AttributeError(
                    "schema_version and schema should not both be specified. If a"
                    " service schema is provided, the schema_version is taken "
                    "from that schema."
                )
            if hasattr(schema, "schema_version"):
                schema_version = getattr(schema, "schema_version")
            else:
                raise TypeError(f"Invalid schema {schema}")

        if schema_version:
            packaging_version.Version(schema_version)

        if not service_version:
            service_version = os.getenv("SERVICE_VERSION") or "0.0.0.dev"

        if "dev" in service_version:
            logging.warning(
                f"The {name} Service is using the development Service "
                f"version {service_version}, ignore this if this"
                f" is a development build."
            )

        self._name = name
        self._schema_version = schema_version
        self._service_version = service_version
        self._started_at = datetime.datetime.now()
        self._has_checked_connections = False
        self._connection_logs = []

        fp = os.path.dirname(os.path.realpath(__file__)) + "/query.graphql"
        with open(fp, "r") as default_query:
            default_query = default_query.read()

        self.manager_http_server = GraphQLHTTPServer.from_api(
            api=GraphQLAPI(root=ServiceManager),
            serve_graphiql=True,
            allow_cors=True,
            root_value=self,
            graphiql_default_query=default_query,
        )

        if self.connect_on_init:
            self.connect()

    def connect(self, timeout: int = None):
        if timeout is None:
            timeout = self.connect_timeout

        if not self._has_checked_connections and self._connections:
            self._has_checked_connections = True

            async def _check_connections(_timeout: int):
                dependencies = []
                for service in self._connections:
                    dependencies.append(
                        service.async_connect(
                            connection_logs=self._connection_logs, timeout=_timeout
                        )
                    )
                await asyncio.gather(*dependencies)

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                loop.create_task(_check_connections(_timeout=timeout))
            else:
                asyncio.run(_check_connections(_timeout=timeout))

    def __getattr__(self, service_name):
        if self._connections:
            for service in self._connections:
                if service.name == service_name:
                    if service.state == ServiceConnectionState.CONNECTION_ERROR:
                        try:
                            loop = asyncio.get_running_loop()
                        except RuntimeError:
                            loop = None

                        if loop and loop.is_running():
                            loop.create_task(service.async_connect())
                        else:
                            asyncio.run(service.async_connect())

                    return service.remote_service

        raise KeyError(f"Service '{service_name}' is not available.")

    def __getitem__(self, item):
        return self.__getattr__(item)

    @field
    def name(self) -> str:
        return self._name

    @field
    def schema_version(self) -> Optional[str]:
        return self._schema_version

    @field
    def service_version(self) -> str:
        return self._service_version

    @field
    def started_at(self) -> str:
        return self._started_at.strftime("%Y-%m-%d %H:%M:%S")

    @field
    def uptime(self) -> str:
        uptime = datetime.datetime.now() - self._started_at
        return str(uptime)

    @field
    def dependencies(self) -> List[ServiceConnection]:
        """
        All the Services this service is dependent on.
        :return:
        """
        return self._connections or []

    @field
    def packages(self) -> List[str]:
        """
        All the Packages this service is dependent on.
        :return:
        """
        import pkg_resources

        installed_packages = pkg_resources.working_set
        installed_packages_list = sorted(
            ["%s==%s" % (i.key, i.version) for i in installed_packages]
        )
        return installed_packages_list

    @field
    def connection_logs(self) -> List[str]:
        return self._connection_logs
