"""OpenTelemetry bootstrap for JobHunter orchestration service."""

import os
import socket
import sys
import logging
from opentelemetry import trace
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import (
    Resource, SERVICE_NAME, SERVICE_NAMESPACE, SERVICE_VERSION,
    DEPLOYMENT_ENVIRONMENT, SERVICE_INSTANCE_ID,
    HOST_NAME, PROCESS_PID, PROCESS_RUNTIME_NAME, PROCESS_RUNTIME_VERSION,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

logger = logging.getLogger(__name__)

def setup_telemetry(app) -> None:
    # 1. Setup Global Propagator for Cross-Service Tracing
    set_global_textmap(TraceContextTextMapPropagator())

    # 2. Resource Definition
    resource = Resource.create({
        SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "jobhunter-orchestration"),
        SERVICE_NAMESPACE: "jobhunter",
        SERVICE_VERSION: os.getenv("APP_VERSION", "1.0.0"),
        DEPLOYMENT_ENVIRONMENT: os.getenv("DEPLOYMENT_ENV", "development"),
        SERVICE_INSTANCE_ID: os.getenv("HOSTNAME", socket.gethostname()),
        HOST_NAME: socket.gethostname(),
        PROCESS_PID: os.getpid(),
        PROCESS_RUNTIME_NAME: "cpython",
        PROCESS_RUNTIME_VERSION: sys.version.split()[0],
    })

    # 3. Tracing Setup (Tempo / OTLP gRPC)
    tracer_provider = TracerProvider(resource=resource)
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint) if otlp_endpoint else ConsoleSpanExporter()
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(tracer_provider)

    # 4. Metrics Setup (Prometheus)
    metric_reader = PrometheusMetricReader()
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    set_meter_provider(meter_provider)

    # 5. Auto-instrumentations (Excluding metrics and health to prevent scrape noise)
    FastAPIInstrumentor.instrument_app(app, excluded_urls=".*/metrics,.*/health")
    HTTPXClientInstrumentor().instrument()
    RedisInstrumentor().instrument()
    BotocoreInstrumentor().instrument()

    logger.info("OpenTelemetry initialised (gRPC endpoint=%s)", otlp_endpoint or "console")

    # 6. Sentry SDK (Error tracking)
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.httpx import HttpxIntegration
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=os.getenv("DEPLOYMENT_ENV", "development"),
            release=os.getenv("APP_VERSION", "1.0.0"),
            traces_sample_rate=0.1,  # Performance traces (can be 0 if using only OTel)
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
                HttpxIntegration(),
            ],
            instrumenter="otel",  # Link Sentry traces with OTel traces
        )
        logger.info("Sentry SDK initialised")


def instrument_sqlalchemy(engine) -> None:
    # Instrument the sync engine for asyncpg compatibility
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
