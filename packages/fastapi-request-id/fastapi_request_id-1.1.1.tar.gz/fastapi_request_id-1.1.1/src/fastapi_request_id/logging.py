import logging
from .context import get_request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        request_id = get_request_id()

        if request_id:
            record.request_id = request_id
        return True
