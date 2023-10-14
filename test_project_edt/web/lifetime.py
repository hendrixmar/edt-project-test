import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse
from kink import di
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_NAME,
    TELEMETRY_SDK_LANGUAGE,
    Resource,
)

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_tracer_provider
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from test_project_edt.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.async_pool = AsyncConnectionPool(conninfo=str(settings.db_url),
                                         kwargs={"row_factory": dict_row},
                                         open=False)
    yield
    await app.async_pool.close()


def create_dependency_container(app: FastAPI):
    di[AsyncConnectionPool] = lambda: lifespan(app)


def setup_opentelemetry(app: FastAPI) -> None:  # pragma: no cover
    """
    Enables opentelemetry instrumentation.

    :param app: current application.
    """
    if not settings.opentelemetry_endpoint:
        return

    tracer_provider = TracerProvider(
        resource=Resource(
            attributes={
                SERVICE_NAME: "test_project_edt",
                TELEMETRY_SDK_LANGUAGE: "python",
                DEPLOYMENT_ENVIRONMENT: settings.environment,
            },
        ),
    )

    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=settings.opentelemetry_endpoint,
                insecure=True,
            ),
        ),
    )

    excluded_endpoints = [
        app.url_path_for("health_check"),
        app.url_path_for("openapi"),
        app.url_path_for("swagger_ui_html"),
        app.url_path_for("swagger_ui_redirect"),
        app.url_path_for("redoc_html"),
    ]

    FastAPIInstrumentor().instrument_app(
        app,
        tracer_provider=tracer_provider,
        excluded_urls=",".join(excluded_endpoints),
    )
    LoggingInstrumentor().instrument(
        tracer_provider=tracer_provider,
        set_logging_format=True,
        log_level=logging.getLevelName(settings.log_level.value),
    )

    set_tracer_provider(tracer_provider=tracer_provider)


def stop_opentelemetry(app: FastAPI) -> None:  # pragma: no cover
    """
    Disables opentelemetry instrumentation.

    :param app: current application.
    """
    if not settings.opentelemetry_endpoint:
        return

    FastAPIInstrumentor().uninstrument_app(app)




def register_startup_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        app.middleware_stack = None
        create_dependency_container(app)
        attach_app_exception_handlers(app)
        setup_opentelemetry(app)
        app.middleware_stack = app.build_middleware_stack()
        pass  # noqa: WPS420

    return _startup



def register_shutdown_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application's shutdown.

    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # noqa: WPS430
        await app.state.db_pool.close()
        stop_opentelemetry(app)
        pass  # noqa: WPS420

    return _shutdown
