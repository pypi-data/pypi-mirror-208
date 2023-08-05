import logging
from .context import get_request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        record.request_id = get_request_id()
        return True
