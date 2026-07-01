"""OpenTelemetry business metrics for JobHunter orchestration service."""

from opentelemetry import metrics

meter = metrics.get_meter("jobhunter-orchestration-business")

# Authentication Metrics
login_total = meter.create_counter(
    "login_total",
    description="Total number of login attempts",
)
login_failure_total = meter.create_counter(
    "login_failure_total",
    description="Total number of failed login attempts",
)
jwt_validation_duration = meter.create_histogram(
    "jwt_validation_duration",
    description="Duration of JWT validation",
    unit="ms",
)
refresh_token_total = meter.create_counter(
    "refresh_token_total",
    description="Total number of refresh token rotations",
)
logout_total = meter.create_counter(
    "logout_total",
    description="Total number of logouts",
)

# Resume Metrics
resume_upload_total = meter.create_counter(
    "resume_upload_total",
    description="Total number of resumes uploaded",
)
resume_generation_total = meter.create_counter(
    "resume_generation_total",
    description="Total number of resumes generated",
)
resume_generation_failed_total = meter.create_counter(
    "resume_generation_failed_total",
    description="Total number of failed resume generations",
)
resume_processing_duration = meter.create_histogram(
    "resume_processing_duration",
    description="Duration of resume processing",
    unit="ms",
)
resume_download_total = meter.create_counter(
    "resume_download_total",
    description="Total number of resumes downloaded",
)

# AI Metrics
ai_request_total = meter.create_counter(
    "ai_request_total",
    description="Total number of AI requests",
)
ai_request_duration = meter.create_histogram(
    "ai_request_duration",
    description="Duration of AI requests",
    unit="ms",
)
ai_failure_total = meter.create_counter(
    "ai_failure_total",
    description="Total number of failed AI requests",
)
ai_retry_total = meter.create_counter(
    "ai_retry_total",
    description="Total number of AI retries",
)
ai_token_input_total = meter.create_counter(
    "ai_token_input_total",
    description="Total number of input tokens used",
)
ai_token_output_total = meter.create_counter(
    "ai_token_output_total",
    description="Total number of output tokens used",
)

# Storage Metrics
minio_upload_total = meter.create_counter(
    "minio_upload_total",
    description="Total number of objects uploaded to MinIO",
)
minio_download_total = meter.create_counter(
    "minio_download_total",
    description="Total number of objects downloaded from MinIO",
)
storage_latency = meter.create_histogram(
    "storage_latency",
    description="Latency of storage operations",
    unit="ms",
)
