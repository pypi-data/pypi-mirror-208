from uuid import uuid4
from .context import (
    get_request_id,
    set_request_id,
)
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request


class RequestContextMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        set_request_id(request.headers.get('X-Request-ID', str(uuid4())))
        response = await call_next(request)
        request_id = get_request_id()

        if request_id:
            response.headers['X-Request-ID'] = request_id

        return response
