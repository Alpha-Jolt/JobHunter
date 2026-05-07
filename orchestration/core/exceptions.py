"""Domain exceptions for the orchestration layer."""


class ApprovalRequiredError(Exception):
    """Raised when a variant has not been approved before sending."""


class DuplicateApplicationError(Exception):
    """Raised when a user has already applied to the same job."""


class RateLimitError(Exception):
    """Raised when daily limit or minimum send interval is exceeded."""


class JobError(Exception):
    """Raised when a job is missing, has no email, or is closed."""


class MailSendError(Exception):
    """Raised when Mail-Bridge fails to send the email."""
