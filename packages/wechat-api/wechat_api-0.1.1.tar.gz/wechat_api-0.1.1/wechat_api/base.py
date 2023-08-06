from abc import ABCMeta
from typing import TYPE_CHECKING, Any, Optional, Union

import httpx

from .exceptions import ApiResponseError

if TYPE_CHECKING:
    from .tools import WechatTools
    from .models.state import WechatState
    from .models.request import RequestMethod


class WechatApi(metaclass=ABCMeta):

    def __init__(self, state: "WechatState", tools: "WechatTools"):
        """ 微信接口封装

        手册地址：
        pay | 微信支付: https://pay.weixin.qq.com/wiki/doc/apiv3/index.shtml
        xwei | 腾讯小微: https://developers.weixin.qq.com/doc/xwei/xiaowei-introduction/Introduction.html
        mini | 小程序: https://developers.weixin.qq.com/miniprogram/dev/framework/
        game | 小游戏: https://developers.weixin.qq.com/minigame/dev/guide/
        offi | 公众号: https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html
        store | 小商店: https://developers.weixin.qq.com/doc/ministore/minishopquickstart/introduction.html
        channels | 视频号: https://developers.weixin.qq.com/doc/channels/Operational_Guidelines/Shop_opening_guidelines.html
        aispeech | 智能对话: https://developers.weixin.qq.com/doc/aispeech/platform/INTRODUCTION.html
        platform | 开放平台: https://developers.weixin.qq.com/doc/oplatform/Third-party_Platforms/2.0/getting_started/terminology_introduce.html
        """
        self.state = state
        self.tools = tools

    def get_api_response_error_info(self, response: "httpx.Response") -> dict:
        try:
            error = response.json()
            error.update({"status": response.status_code})
            return error
        except Exception:
            return {
                "status": response.status_code,
                "content": response.text
            }

    def get_response_info(self, response: "httpx.Response", fields: list = None) -> Union[dict, str, int]:
        res = response.json()
        if res.get('errcode') != 0:
            return self.get_api_response_error_info(response)
        if fields is not None:
            if len(fields) == 1:
                return res.get(fields[0])
            return {field: res.get(field) for field in fields}
        return res

    def call_api(
            self,
            package_name: str,
            app_name: str,
            method: "RequestMethod",
            path: str,
            /, *,
            data: Optional[dict[str, Any]] = None,
            params: Optional[dict[str, Any]] = None,
            headers: Optional[dict[str, str]] = None,
            **kwargs
    ) -> "httpx.Response":
        """ 同步调用指定的微信 Api 接口 """
        method = method.upper()
        headers = headers or {}

        context = {
            "package_name": package_name,
            "app_name": app_name,
            "method": method,
            "path": path,
            "data": data,
            "params": params,
            "headers": headers,
            "kwargs": kwargs,
        }
        package = getattr(self.state, package_name)
        if not hasattr(package, "base_url"):
            raise ApiResponseError(f"wechat package {package_name} 未设置接口请求域名", context=context)

        try:
            response = httpx.request(url=f"{package.base_url}{path}", json=data, method=method, params=params, headers=headers)
            return response
        except httpx.HTTPError as e:
            context.update({"reqeust": e.request})
            raise ApiResponseError(str(e), context=context)
        except httpx.CookieConflict as e:
            raise ApiResponseError(str(e), context=context)
        except httpx.StreamError as e:
            raise ApiResponseError(str(e), context=context)
        except httpx.InvalidURL as e:
            raise ApiResponseError(str(e), context=context)

    async def acall_api(
        self,
        package_name: str,
        app_name: str,
        method: "RequestMethod",
        path: str,
        /, *,
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        **kwargs
    ) -> "httpx.Response":
        """ 异步调用指定的微信 Api 接口 """
        method = method.upper()
        headers = headers or {}

        context = {
            "package_name": package_name,
            "app_name": app_name,
            "method": method,
            "path": path,
            "data": data,
            "params": params,
            "headers": headers,
            "kwargs": kwargs,
        }
        package = getattr(self.state, package_name)
        if not hasattr(package, "base_url"):
            raise ApiResponseError(f"wechat package {package_name} 未设置接口请求域名", context=context)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(url=f"{package.base_url}{path}", json=data, method=method, params=params, headers=headers)
                return response
        except httpx.HTTPError as e:
            context.update({"reqeust": e.request})
            raise ApiResponseError(str(e), context=context)
        except httpx.CookieConflict as e:
            raise ApiResponseError(str(e), context=context)
        except httpx.StreamError as e:
            raise ApiResponseError(str(e), context=context)
        except httpx.InvalidURL as e:
            raise ApiResponseError(str(e), context=context)
