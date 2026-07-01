"""OpenTelemetry bootstrap for JobHunter orchestration service."""

import os
import logging
from opentelemetry import trace
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
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
    resource = Resource.create({SERVICE_NAME: "jobhunter-orchestration"})

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


def instrument_sqlalchemy(engine) -> None:
    # Instrument the sync engine for asyncpg compatibility
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
