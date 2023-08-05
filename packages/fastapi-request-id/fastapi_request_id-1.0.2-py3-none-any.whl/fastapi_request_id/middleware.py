from uuid import uuid4
from .context import (
    get_request_id,
    set_request_id,
    reset_request_id,
)
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request


class RequestContextMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        request_token = set_request_id(request.headers.get('X-Request-ID', str(uuid4())))

        try:
            response = await call_next(request)
        except Exception as error:
            setattr(error, '__request_id__', get_request_id())
            reset_request_id(request_token)
            raise error

        response.headers['X-Request-ID'] = get_request_id()

        reset_request_id(request_token)

        return response
