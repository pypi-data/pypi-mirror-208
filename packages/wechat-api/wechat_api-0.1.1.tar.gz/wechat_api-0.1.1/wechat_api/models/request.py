from typing import Any, Union, Literal, Optional

from pydantic import BaseModel

# from django.core.handlers.wsgi import WSGIRequest as DWSGIRequest
# from django.core.handlers.asgi import ASGIRequest as DASGIRequest
# from rest_framework.request import Request as DRFRequest


RequestMethod = Literal["get", "post", "put", "patch", "delete", "options"]
RequestMethodUpper = Literal["GET", "POST", "PUT", "PATH", "DELETE"]
RequestScheme = Literal["http", "https", "ws", "wss"]


# class Request(DRFRequest):
#     id: str
#     start_time: Optional[int]


# class WSGIRequest(DWSGIRequest):
#     id: str
#     start_time: Optional[int]


# class ASGIRequest(DASGIRequest):
#     id: str
#     start_time: Optional[int]


class RequestLogInfo(BaseModel):
    id: str
    path: str
    data: Optional[Any]
    query: str
    scheme: RequestScheme
    method: Union[RequestMethod, Literal[""]]
    headers: Optional[dict[str, str]]
    client_ip: str


class ResponseLogInfo(RequestLogInfo):
    status: int
    request_time: int
    response_headers: Optional[dict[str, str]]
