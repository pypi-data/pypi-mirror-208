from typing import Optional

from pydantic import BaseModel


class PlatformAccessToken(BaseModel):
    scope: str
    openid: str
    unionid: str
    expires_in: int
    access_token: str
    refresh_token: str


class PlatformUserInfo(BaseModel):
    openid: str
    nickname: str
    sex: int
    province: str
    city: str
    country: str
    headimgurl: str
    privilege: Optional[list[str]]
    unionid: str

