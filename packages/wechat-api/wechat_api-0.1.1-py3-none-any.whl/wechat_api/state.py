from .models.state import WechatState


class _WechatState:
    __instance = None

    def __new__(cls, settings: dict) -> "WechatState":
        if not cls.__instance:
            cls.__instance = WechatState(**settings)

        return cls.__instance
