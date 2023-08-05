from abc import ABC, abstractmethod
from fastapi_request_id import get_request_id

from fastapi import Request, Response


class BaseExceptionHandler(ABC):

    def __call__(self, request: Request, exc: Exception):
        request_id = get_request_id()
        response = self.build_response(request, exc)

        if request_id:
            response.headers['X-Request-ID'] = request_id

        return response

    @staticmethod
    @abstractmethod
    def build_response(request: Request, exc: Exception) -> Response:
        ...
