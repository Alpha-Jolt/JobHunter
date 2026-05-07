# orchestration/core/logging_setup.py

import logging
import json
from datetime import datetime
import sys

def setup_logging(log_level: str = 'INFO', log_format: str = 'json'):
    """
    Setup structured logging for the application.
    
    Args:
        log_level: DEBUG, INFO, WARNING, ERROR
        log_format: 'json' for structured, 'text' for human-readable
    """
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    if log_format == 'json':
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    try:
        file_handler = logging.FileHandler('logs/api.log')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        root_logger.warning(f'Could not setup file logging: {e}')


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_dict = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, 'user_id'):
            log_dict['user_id'] = record.user_id
        if hasattr(record, 'job_id'):
            log_dict['job_id'] = record.job_id
        if hasattr(record, 'variant_id'):
            log_dict['variant_id'] = record.variant_id

        # Add exception if present
        if record.exc_info:
            log_dict['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_dict, default=str)