from typing import Optional

from pydantic import BaseModel


class ErrorInfo(BaseModel):
    code: Optional[str]
    desc: Optional[str]
    status: Optional[int]
    solution: Optional[str]


class WechatError(Exception):
    msg: str
    type: str = "base"
    context: Optional[dict]

    def __init__(self, msg: str, context: Optional[dict] = None):
        self.msg = msg
        self.context = context

    def __str__(self):
        return self.msg


class DecryptError(WechatError):
    type = "decrypt"


class AppImportError(WechatError):
    type = "app_import"


class ValidationError(WechatError):
    type = "validation"


class ApiResponseError(WechatError):
    type: str = "api_response"

    def __init__(
        self,
        msg: str,
        context: dict,
        error: Optional[dict] = None,
    ):
        self.msg = msg
        self.error = error
        self.context = {**context, "error": self.error if error else {}}


class LoadPrivateKeyError(WechatError):
    type = "load_private_key"


class GenerateSignatureError(WechatError):
    type = "generate_signature"
