from typing import Optional

from pydantic import BaseModel


class MiniUserSession(BaseModel):
    openid: str
    unionid: Optional[str]
    session_key: str


class WaterMark(BaseModel):
    timestamp: int
    appid: str


class MiniUserPhone(BaseModel):
    watermark: WaterMark
    countryCode: str
    phoneNumber: str
    purePhoneNumber: str


class FormData(BaseModel):
    filename: Optional[str]
    filelength: Optional[int]
    contentType: str
    value: bytes
