import sys
from typing import Optional, TYPE_CHECKING

from .base import WechatApi
from .state import _WechatState
from .tools import WechatTools
from .pay import WechatPayApi
from .mini import WechatMiniApi
from .platform import WechatPlatformApi
from .offi import WechatOffiApi


if TYPE_CHECKING:
    from .models.state import WechatState


class Wechat:
    __instance = None
    state: Optional["WechatState"] = None
    tools: Optional["WechatTools"] = None
    pay: Optional["WechatPayApi"] = None
    mini: Optional["WechatMiniApi"] = None
    game: Optional["WechatApi"] = None
    work: Optional["WechatApi"] = None
    xwei: Optional["WechatApi"] = None
    store: Optional["WechatApi"] = None
    aispeech: Optional["WechatApi"] = None
    channels: Optional["WechatApi"] = None
    platform: Optional["WechatPlatformApi"] = None
    offi: Optional["WechatOffiApi"] = None
    packages = ["pay", "mini", "game", "work", "xwei", "store", "aispeech", "channels", "platform", "offi"]

    def __new__(cls, settings: dict) -> "Wechat":
        """ 微信接口核心类

        通过此类将微信全部可用接口聚合到一起形成一个单例模式，后续通过一处实例化即可全局使用

        Args:
            settings: 配置项
        """
        if not cls.__instance:
            cls.state = _WechatState(settings)
            cls.tools = WechatTools(cls.state)

            modules = sys.modules[__name__]
            for package in cls.packages:
                if package in settings.keys():
                    package_class = getattr(modules, f"Wechat{package.capitalize()}Api", WechatApi)
                    setattr(cls, package, package_class(cls.state, cls.tools))

            # 释放内存
            del modules
            cls.__instance = object.__new__(cls)

        return cls.__instance
