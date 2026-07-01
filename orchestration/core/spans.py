"""Custom decoupled tracing wrapper for JobHunter."""

from contextlib import asynccontextmanager
from opentelemetry import trace

@asynccontextmanager
async def traced(operation_name: str, **attributes):
    tracer = trace.get_tracer("jobhunter.orchestration")
    with tracer.start_as_current_span(operation_name) as span:
        for k, v in attributes.items():
            span.set_attribute(k, str(v))
        yield span
