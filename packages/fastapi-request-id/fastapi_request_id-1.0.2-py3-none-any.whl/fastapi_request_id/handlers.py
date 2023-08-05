from abc import ABC, abstractmethod
from typing import Optional

from fastapi import Request, Response


class BaseExceptionHandler(ABC):

    def __call__(self, request: Request, exc: Exception):
        request_id = getattr(exc, '__request_id__', None)
        delattr(exc, '__request_id__')
        response = self.build_response(request, exc, request_id)

        if request_id:
            response.headers['X-Request-ID'] = request_id

        return response

    @staticmethod
    @abstractmethod
    def build_response(request: Request, exc: Exception, request_id: Optional[str]) -> Response:
        ...
