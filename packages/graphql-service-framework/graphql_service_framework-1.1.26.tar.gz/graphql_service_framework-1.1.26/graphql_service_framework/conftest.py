import pytest

from context_helper import Context, ctx as _ctx
from typing import Dict


@pytest.fixture
def ctx():
    yield _ctx


@pytest.fixture
def services_ctx():
    class MockServicesManager:
        def __init__(self, services: Dict = None):
            self.services = services or {}

        def add_service(self, name: str, service):
            self.services[name] = service

        def __getattr__(self, service_name):
            return self.services.get(service_name)

    context = Context(services=MockServicesManager())
    context.push()
    yield context
    context.pop()
