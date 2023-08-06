import time
import json
import uuid
from typing import Any, Optional
from pathlib import Path

import httpx

from .models.base import TimedeltaParams

from .base import WechatApi
from .exceptions import ApiResponseError
from .models.pay import MiniPayInfo, TransactionInfo


class WechatPayApi(WechatApi):

    def get_authorization_header(
        self,
        method: str,
        url: str,
        data: Optional[Any] = None,
        nonce_str: Optional[str] = None,
        timestamp: Optional[str] = None
    ) -> str:
        """ 根据要求生成微信支付需要的 Authorization Http Header """
        timestamp = timestamp or str(int(time.time()))
        nonce_str = nonce_str or uuid.uuid4().hex.upper()
        body = data if isinstance(data, str) else (json.dumps(data) if data else "")
        sign_str = "\n".join([method.upper(), url, timestamp, nonce_str, body]) + "\n"
        private_key = self.tools.load_private_key(cert_path=Path(self.state.cert_path) / "apiclient_key.pem")
        signature = self.tools.generate_rsa_sign(private_key, sign_str)
        return f'WECHATPAY2-SHA256-RSA2048 mchid="{self.state.pay.mch_id}",serial_no="{self.state.pay.serial_no}",nonce_str="{nonce_str}",timestamp="{timestamp}",signature="{signature}"'

    def pay_transactions_jsapi(
        self,
        package_name: str,
        app_name: str,
        openid: str,
        amount: int,
        out_trade_no: str,
        description: str,
        attach: str = "",
        time_expire: Optional["TimedeltaParams"] = None
    ) -> str:
        """ 微信支付 JSAPI 下单

        商户系统先调用该接口在微信支付服务后台生成预支付交易单，
        返回正确的预支付交易会话标识后再按 Native、JSAPI、APP 等不同场景生成交易串调起支付。
        """
        app = self.tools.get_app(package_name, app_name)
        path = "/v3/pay/transactions/jsapi"
        time_expire = time_expire if time_expire else {"hours": 2}
        pay_info = {
            "appid": app.app_id,
            "mchid": self.state.pay.mch_id,
            "description": description,
            "out_trade_no": out_trade_no,
            "time_expire": self.tools.get_rfc3339_time(**time_expire),
            "attach": attach,
            "notify_url": self.state.pay.callback_url.get("jsapi"),
            "support_fapiao": False,
            "amount": {
                "total": amount,
                "currency": "CNY"
            },
            "payer": {
                "openid": openid
            },
        }

        response = self.call_api(package_name, app_name, "post", path, data=pay_info)

        return response.json().get("prepay_id")

    def pay_transactions_native(
        self,
        package_name: str,
        app_name: str,
        amount: int,
        payer_client_ip: str,
        description: str,
        out_trade_no: str,
        attach: str = "",
        time_expire: Optional["TimedeltaParams"] = None
    ) -> str:
        """ 微信支付 Native 下单 API

        商户 Native 支付下单接口，微信后台系统返回链接参数 code_url，商户后台系统将 code_url 值生成二维码图片，用户使用微信客户端扫码后发起支付。
        """
        app = self.tools.get_app(package_name, app_name)
        path = "/v3/pay/transactions/native"
        time_expire = time_expire if time_expire else {"hours": 2}
        pay_info = {
            "appid": app.app_id,
            "mchid": self.state.pay.mch_id,
            "description": description,
            "out_trade_no": out_trade_no,
            "time_expire": self.tools.get_rfc3339_time(**time_expire),
            "attach": attach,
            "notify_url": self.state.pay.callback_url.get("native"),
            "support_fapiao": False,
            "amount": {
                "total": amount,
                "currency": "CNY"
            },
            "scene_info": {
                "payer_client_ip": payer_client_ip
            },
        }

        response = self.call_api(package_name, app_name, "post", path, data=pay_info)

        return response.json().get("code_url")

    def get_mini_pay_info(
        self,
        openid: str,
        amount: int,
        description: str,
        out_trade_no: str,
        attach: str = "",
        app_name: str = "doraemon",
        time_expire: Optional["TimedeltaParams"] = None
    ) -> "MiniPayInfo":
        """ 通过 wechat jsapi api 下单后生成小程序使用的支付信息  """
        prepay_id = self.pay_transactions_jsapi(
            package_name="mini", app_name=app_name, openid=openid, amount=amount,
            description=description, out_trade_no=out_trade_no, attach=attach,
            time_expire=time_expire
        )
        timestamp = str(int(time.time()))
        nonce_str = self.tools.get_random_string()
        sign_str = f"{self.state.mini.apps.get('doraemon').app_id}\n{timestamp}\n{nonce_str}\nprepay_id={prepay_id}\n"
        private_key = self.tools.load_private_key(Path(self.state.cert_path) / "apiclient_key.pem")
        signature = self.tools.generate_rsa_sign(private_key, sign_str)

        pay_info = {
            "paySign": signature,
            "package": f"prepay_id={prepay_id}",
            "nonceStr": nonce_str,
            "timeStamp": timestamp,
        }

        return MiniPayInfo(**pay_info)

    def get_the_transaction_info(self, package_name: str, app_name: str, id: str) -> "TransactionInfo":
        path = f"/v3/pay/transactions/out-trade-no/{id}"
        params = {
            "mchid": self.state.pay.mch_id
        }

        response = self.call_api(package_name, app_name, "get", path, params=params)

        return TransactionInfo(**response.json())

    def close_the_transaction(self, id: str):
        path = f"/v3/pay/transactions/out-trade-no/{id}/close"
        data = {
            "mchid": self.state.pay.mch_id
        }

        headers = {
            "Authorization": self.get_authorization_header("POST", path, data=data)
        }
        response = self.call_api("pay", "", "post", path, data=data, headers=headers)

        if response.status_code != 204:
            raise ApiResponseError("服务器接口响应失败", context={"response": response}, error=self.get_api_response_error_info(response))

        return True
