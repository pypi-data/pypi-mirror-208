from typing import Dict, Union, Optional
from pathlib import Path

from pydantic import BaseModel


class WechatApp(BaseModel):
    app_id: str
    secret_key: str


class WechatPackage(BaseModel):
    apps: Dict[str, WechatApp] = {}
    base_url: Optional[str]


class Pay(WechatPackage):
    mch_id: str
    v2_key: str
    v3_key: str
    base_url: str
    serial_no: str
    callback_url: Dict[str, str] = {}


class Mini(WechatPackage):
    pass


class OffiApp(WechatApp):
    token: str


class Offi(WechatPackage):
    apps: Dict[str, OffiApp] = {}


class Platform(WechatPackage):
    pass


class WechatState(BaseModel):
    pay: Optional[Pay]
    mini: Optional[Mini]
    offi: Optional[Offi]
    game: Optional[WechatPackage]
    work: Optional[WechatPackage]
    xwei: Optional[WechatPackage]
    store: Optional[WechatPackage]
    aispeech: Optional[WechatPackage]
    channels: Optional[WechatPackage]
    platform: Optional[Platform]
    cert_path: Union[Path, str]

    @staticmethod
    def get_app_from_package(package: "WechatPackage", app_name: str) -> Optional["WechatApp"]:
        return package.apps.get(app_name, None)

    def get_package(self, package_name: str) -> Optional["WechatPackage"]:
        wechat_package = getattr(self, package_name, None)

        if not isinstance(wechat_package, WechatPackage):
            return None

        return wechat_package

    def get_app(self, package_name: str, app_name: str) -> Optional["WechatApp"]:
        wechat_package = getattr(self, package_name, None)

        if not isinstance(wechat_package, WechatPackage):
            return None

        wechat_app = wechat_package.apps.get(app_name, None)

        if not isinstance(wechat_app, WechatApp):
            return None

        return wechat_app
