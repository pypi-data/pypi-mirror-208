from typing import Dict, Callable, Iterable

from context_helper import Context
from werkzeug import Request

from graphql_service_framework.mesh import ServiceManager
from graphql_service_framework.service import WSGIFramework


class ServiceMeshMiddleware:
    def __init__(
        self,
        wsgi_app: WSGIFramework,
        service_manager: "ServiceManager",
        service_manager_path: str = None,
        check_connections_on_first_request: bool = True,
        context_key: str = "services",
    ):
        self.wsgi_app = wsgi_app
        self.service_manager = service_manager
        self.service_manager_path = service_manager_path
        self.connect_on_first_request = check_connections_on_first_request
        self.context_key = context_key

    def __call__(self, environ: Dict, start_response: Callable) -> Iterable[bytes]:
        if self.connect_on_first_request:
            self.service_manager.connect()

        request = Request(environ)

        if request.path == f"{self.service_manager_path}":
            # Expose the service manager HTTP server
            return self.service_manager.manager_http_server.app()(
                environ, start_response
            )

        with Context(**{self.context_key: self.service_manager}):
            return self.wsgi_app(environ, start_response)
