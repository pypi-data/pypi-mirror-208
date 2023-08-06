import inspect
import logging
import os

from typing import TypeVar, Optional, Type, Dict

from graphql import print_schema, GraphQLSchema
from graphql_api.utils import to_snake_case

from schemadiff import diff, format_diff
from schemadiff.changes import CriticalityLevel

from graphql_api.api import GraphQLRootTypeDelegate
from graphql_api import GraphQLAPI
from graphql_api.remote import GraphQLRemoteExecutor, GraphQLRemoteObject

TClient = TypeVar("TClient", bound="Schema")

"""
Schema Provides Utilities to help with a Service

Schema Class Attributes:
    api_version         The version of this schema, this must be defined
                        in the root controller.

    validate_schema     When set to `True` a check will be run on any
                        implementations of this service and check they
                        adhere to the schema

    criticality         If `validate_schema` is True an exception will be
                        raised if any changes meet or exceed this level.
                        If `validate_schema` is True and `criticality` is
                        set to `None` an exception will not be raised but
                        the changes will still be logged.
"""


class SchemaVersion(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return super().__prepare__(name, bases, **kwargs)

    def __new__(mcs, name, bases, namespace, **kwargs):
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, schema_version=None, **kwargs):
        if schema_version:
            cls.schema_version = schema_version
        else:
            for base in bases:
                if hasattr(base, "schema_version") and base.schema_version:
                    cls.schema_version = base.schema_version

        if not cls.schema_version:
            cls.schema_version = "0.0.1.dev"
        super().__init__(name, bases, namespace)


class Schema(GraphQLRootTypeDelegate, metaclass=SchemaVersion):
    schema_version: str = None
    validate_schema: bool = True
    criticality: Optional[CriticalityLevel] = CriticalityLevel.NonBreaking
    ignore_description_changes: bool = True

    def __init__(self, config: Dict = None, url: str = None):
        if not config:
            config = {}
        self.config = config
        self.url = url

    def __new__(cls, config: Dict = None, url: str = None, *args, **kwargs):
        schema_class = cls.get_schema_class()
        if cls == schema_class:
            return cls.client(url=url)

        return super(Schema, cls).__new__(cls)

    @classmethod
    def get_schema_class(cls):
        bases = list(inspect.getmro(cls))
        reversed_bases = list(reversed(bases))
        found_schema = False
        for base in reversed_bases:
            if found_schema:
                return base
            if base == Schema:
                found_schema = True

    @classmethod
    def validate_graphql_schema(cls, schema: GraphQLSchema) -> GraphQLSchema:
        if cls.validate_schema:
            bases = list(inspect.getmro(cls))
            reversed_bases = list(reversed(bases))
            schema_class: Optional[Type[Schema]] = None
            for base in reversed_bases:
                if issubclass(base, Schema) and base != Schema:
                    schema_class = base
                    break
            if schema_class == reversed_bases[-1]:
                # This is a schema - no need to validate
                return schema

            if schema_class:
                validate(
                    schema,
                    schema_class,
                    cls.criticality,
                    cls.ignore_description_changes,
                )

        return schema

    @classmethod
    def client(cls: TClient, url: str = None) -> TClient:
        if not url:
            name = to_snake_case(cls.__name__).upper()
            env_var = f"{name}_URL"
            url = os.getenv(env_var)
            if not url:
                raise ValueError(
                    f"A URL for client {cls.__name__} could not be found. "
                    f"Please set the `{env_var}` environment variable or "
                    f"specify a URL when creating the {cls.__name__} client"
                )
        # noinspection PyTypeChecker
        return GraphQLRemoteObject(
            executor=GraphQLRemoteExecutor(url, name=cls.__name__),
            api=GraphQLAPI(root=cls),
        )

    @classmethod
    def graphql_schema(cls) -> GraphQLSchema:
        return GraphQLAPI(root=cls).graphql_schema()[0]

    def create_service(self, config: Dict = None):
        from graphql_service_framework import Service

        return Service(root=self, config={**self.config, **(config or {})})


def validate(
    graphql_schema: GraphQLSchema,
    service_schema: Type[Schema],
    criticality: CriticalityLevel,
    ignore_description_changes: bool = True,
):
    generated_service_schema = GraphQLAPI(root=service_schema).graphql_schema()[0]

    if not generated_service_schema:
        raise ValueError(f"Could not generate service schema for {service_schema}")
    query_a = generated_service_schema.query_type
    query_b = graphql_schema.query_type

    if query_a and query_b and query_a.name != query_b.name:
        query_a.name = query_b.name

    mutation_a = generated_service_schema.query_type
    mutation_b = graphql_schema.query_type

    if mutation_a and mutation_b and mutation_a.name != mutation_b.name:
        mutation_a.name = mutation_b.name

    generated_service_schema_language = print_schema(generated_service_schema)

    schema_language = print_schema(graphql_schema)

    # There should be no changes for a perfect implementation
    changes = diff(generated_service_schema_language, schema_language)

    # Ignore description changes as often they are uncontrollable
    if ignore_description_changes:
        changes = [
            change
            for change in changes
            if "DescriptionChanged" not in type(change).__name__
        ]

    if changes:
        raise_error_map = {
            None: [],
            CriticalityLevel.NonBreaking: [
                CriticalityLevel.NonBreaking,
                CriticalityLevel.Dangerous,
                CriticalityLevel.Breaking,
            ],
            CriticalityLevel.Dangerous: [
                CriticalityLevel.Dangerous,
                CriticalityLevel.Breaking,
            ],
            CriticalityLevel.Breaking: [CriticalityLevel.Breaking],
        }

        raise_err = any(
            change.criticality.level in raise_error_map[criticality]
            for change in changes
        )

        format_changes = format_diff(changes)

        if raise_err:
            raise TypeError(
                f"Validation Error\n The service "
                f"`{graphql_schema.query_type.name}` does not adhere to "
                f"`{service_schema.__name__}` version "
                f"'{service_schema.schema_version}', here are the changes:\n"
                f"{format_changes}\n You may be able to suppress this error by"
                f" setting the class attribute "
                f"`{graphql_schema.query_type.name}.validate_schema` to False,"
                f" or by lowering the "
                f"`{graphql_schema.query_type.name}.criticality`."
            )
        else:
            logging.warning(
                f"Validation Error\n"
                f"The service `{graphql_schema.query_type.name}` does not "
                f"adhere to `{service_schema.__name__}` version "
                f"'{service_schema.schema_version}', here are the "
                f"changes:\n {format_changes}\n"
            )

    if "dev" in service_schema.schema_version:
        logging.warning(
            f"The {service_schema.__name__} Schema is using the development "
            f"Schema version {service_schema.schema_version}, ignore this if this"
            f" is a development build."
        )
