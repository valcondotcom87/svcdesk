"""Logging helpers for structured logs with request ids."""
import json
import logging
from datetime import datetime, timezone as dt_timezone

from apps.core.middleware import get_request_id


class RequestIdFilter(logging.Filter):
    """Attach request_id to log records when available."""

    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):
    """Simple JSON formatter for structured logging."""

    def format(self, record):
        payload = {
            'timestamp': datetime.fromtimestamp(record.created, tz=dt_timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'request_id': getattr(record, 'request_id', None),
        }
        if hasattr(record, 'method'):
            payload['method'] = record.method
        if hasattr(record, 'path'):
            payload['path'] = record.path
        if hasattr(record, 'status_code'):
            payload['status_code'] = record.status_code
        if hasattr(record, 'remote_addr'):
            payload['remote_addr'] = record.remote_addr
        if record.exc_info:
            payload['exception'] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)
