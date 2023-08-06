import json
import datetime
import time
from typing import Union
from urllib.parse import urlencode

from .base import WechatApi
from .models.base import Token
from .models.mini import MiniUserPhone, MiniUserSession, FormData
from .exceptions import DecryptError, ValidationError


class WechatMiniApi(WechatApi):
    tokens: dict[str, "Token"] = {}
    stable_tokens: dict[str, "Token"] = {}

    def decrypt(self, iv: str, key: str, data: str, app_name: str = "doraemon") -> dict:
        """ 解密微信加密的内容

        文档：https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/signature.html
        """
        try:
            decrypt_data = self.tools.decrypt_aes(iv=iv, key=key, data=data)
            decrypt_data = decrypt_data[:-ord(decrypt_data[len(decrypt_data) - 1:])]

            try:
                decrypt_data = json.loads(decrypt_data)
            except (ValueError, json.JSONDecodeError) as e:
                raise DecryptError("解密数据格式错误", context={"decrypt_data": decrypt_data}) from e

            if not decrypt_data.get("watermark") or decrypt_data["watermark"]["appid"] != self.tools.get_app("mini",
                                                                                                             app_name).app_id:
                raise DecryptError("加密水印与解密主体不符", context={"decrypt_data": decrypt_data})

            return decrypt_data
        except Exception as e:
            raise DecryptError("解密失败") from e

    def get_access_token(self, app_name: str = "doraemon") -> str:
        """ 获取小程序全局唯一后台接口调用凭据并缓存到本地 """
        token_info = self.tokens.get(app_name)

        if token_info and token_info.expires_on > datetime.datetime.now():
            return token_info.token

        app = self.tools.get_app("mini", app_name)
        path = "/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": app.app_id,
            "secret": app.secret_key,
        }

        response = self.call_api("mini", app_name, "get", path, params=params)
        result = response.json()

        self.tokens[app_name] = Token(
            token=result.get("access_token"),
            expires_on=datetime.datetime.now() + datetime.timedelta(seconds=int(result.get("expires_in", 0)))
        )
        return result.get("access_token")

    def get_stable_access_token(self, force_refresh=False, app_name: str = "doraemon") -> str:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-access-token/getStableAccessToken.html
        获取小程序全局后台接口调用凭据，有效期最长为7200s
        """
        token_info = self.stable_tokens.get(app_name)

        if token_info and token_info.expires_on > datetime.datetime.now():
            return token_info.token

        app = self.tools.get_app("mini", app_name)
        path = "/cgi-bin/stable_token"
        data = {
            "grant_type": "client_credential",
            "appid": app.app_id,
            "secret": app.secret_key,
            "force_refresh": force_refresh
        }
        response = self.call_api("mini", app_name, "post", path, data=data)
        result = response.json()

        self.stable_tokens[app_name] = Token(
            token=result.get("access_token"),
            expires_on=datetime.datetime.now() + datetime.timedelta(seconds=int(result.get("expires_in", 0)))
        )
        return result.get("access_token")

    def clear_quota(self, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/openApi-mgnt/clearQuota.html
        本接口用于清空公众号/小程序/第三方平台等接口的每日调用接口次数
        """
        path = "/cgi-bin/clear_quota"
        params = {
            "access_token": self.get_access_token(app_name)
        }
        app = self.tools.get_app("mini", app_name)
        data = {
            "appid": app.app_id
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def get_api_quota(self, cgi_path: str, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/openApi-mgnt/getApiQuota.html
        本接口用于查询公众号/小程序/第三方平台等接口的每日调用接口的额度以及调用次数
        """
        path = "/cgi-bin/openapi/quota/get"
        params = {
            "access_token": self.get_access_token(app_name)
        }
        data = {
            "cgi_path": cgi_path
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def get_rid_info(self, rid: str, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/openApi-mgnt/getRidInfo.html
        本接口用于查询调用公众号/小程序/第三方平台等接口报错返回的rid详情信息，辅助开发者高效定位问题
        """
        path = "/cgi-bin/openapi/rid/get"
        params = {
            "access_token": self.get_access_token(app_name)
        }
        data = {
            "rid": rid
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def clear_quota_by_app_secret(self, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/openApi-mgnt/clearQuotaByAppSecret.html
        本接口用于清空公众号/小程序等接口的每日调用接口次数
        """
        path = "/cgi-bin/clear_quota/v2"
        app = self.tools.get_app("mini", app_name)
        params = {
            "appid": app.app_id,
            "appsecret": app.secret_key
        }
        response = self.call_api("mini", app_name, "post", path, params=params)
        return self.get_response_info(response)

    def get_plugin_open_pid(self, code: str, app_name: str = "doraemon") -> Union[str, dict]:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-info/basic-info/getPluginOpenPId.html
        通过 wx.pluginLogin 接口获得插件用户标志凭证 code 后传到开发者服务器，开发者服务器调用此接口换取插件用户的唯一标识 openpid
        """
        path = "/wxa/getpluginopenpid"
        params = {
            "access_token": self.get_access_token(app_name)
        }
        data = {
            "code": code
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response, fields=["openid"])

    def check_encrypted_data(self, encrypted_msg_hash: str, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-info/basic-info/checkEncryptedData.html
        检查加密信息是否由微信生成（当前只支持手机号加密数据），只能检测最近3天生成的加密数据
        """
        path = "/wxa/business/checkencryptedmsg"
        params = {
            "access_token": self.get_access_token(app_name)
        }
        data = {
            "encrypted_msg_hash": encrypted_msg_hash
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def get_paid_unionid(
            self,
            openid: str,
            transaction_id: str = None,
            mch_id: str = None,
            out_trade_no: str = None,
            app_name: str = "doraemon"
    ) -> Union[dict, str]:
        """
        不可用
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-info/basic-info/getPaidUnionid.html
        该接口用于在用户支付完成后，获调用本接口前需要用户完成支付，用户支付完成后，取该用户的 UnionId，无需用户授权。本接口支付后的五分钟内有效。
        """
        path = "/wxa/getpaidunionid"
        params = {
            "access_token": self.get_access_token(app_name),
            "openid": openid,
            "transaction_id": transaction_id,
            "mch_id": mch_id,
            "out_trade_no": out_trade_no
        }
        response = self.call_api("mini", app_name, "get", path, params=params)
        return self.get_response_info(response, fields=["unionid"])

    def get_user_encrypt_key(
            self,
            openid: str,
            signature: str,
            sig_method: str,
            app_name: str = "doraemon"
    ) -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-info/internet/getUserEncryptKey.html
        该接口用于获取用户encryptKey。 会获取用户最近3次的key，每个key的存活时间为3600s。
        """
        path = "/wxa/business/getuserencryptkey"
        params = {
            "access_token": self.get_access_token(app_name)
        }
        data = {
            "openid": openid,
            "signature": signature,
            "sig_method": sig_method
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response, fields=["key_info_list"])

    def get_user_session(self, code: str, app_name: str = "doraemon") -> "MiniUserSession":
        """ 登录凭证校验

        通过 wx.login 接口获得临时登录凭证 code 后传到开发者服务器调用此接口完成登录流程。
        文档：https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-login/code2Session.html
        """
        if not code:
            raise ValidationError("未传入临时登录凭证 code")

        app = self.tools.get_app("mini", app_name)
        path = "/sns/jscode2session"
        params = {
            "appid": app.app_id,
            "secret": app.secret_key,
            "js_code": code,
            "grant_type": "authorization_code",
        }

        response = self.call_api("mini", app_name, "get", path, params=params)

        return MiniUserSession(**response.json())

    def get_user_phone(self, code: str, app_name: str = "doraemon") -> "MiniUserPhone":
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-info/phone-number/getPhoneNumber.html
        该接口用于将code换取用户手机号。 说明，每个code只能使用一次，code的有效期为5min
        """
        if not code:
            raise ValidationError("未传入用户登录凭证")

        path = "/wxa/business/getuserphonenumber"
        params = {
            "access_token": self.get_access_token(app_name)
        }
        data = {
            "code": code,
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)

        return MiniUserPhone(**response.json().get("phone_info"))

    def get_qr_code(
            self,
            path: str,
            width: int = 430,
            auto_color: bool = False,
            line_color: dict[str, int] = {"r": 0, "g": 0, "b": 0},
            env_version: str = "release",
            app_name: str = "doraemon"
    ) -> Union[dict, bytes]:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/qrcode-link/qr-code/getQRCode.html
        该接口用于获取小程序码，适用于需要的码数量较少的业务场景。通过该接口生成的小程序码，永久有效，有数量限制
        详见: https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/qr-code.html
        """
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        data = {
            "path": path,
            "width": width,
            "auto_color": auto_color,
            "line_color": line_color,
            "env_version": env_version
        }
        path = "/wxa/getwxacode"
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        try:
            response.json()
            return self.get_api_response_error_info(response)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return response.content

    def get_unlimited_qr_code(
            self,
            scene: str,
            path: str = None,
            check_path: bool = True,
            env_version: str = "release",
            width: int = 430,
            auto_color: bool = False,
            line_color: dict[str, int] = {"r": 0, "g": 0, "b": 0},
            is_hyaline: bool = False,
            app_name: str = "doraemon"
    ) -> Union[dict, bytes]:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/qrcode-link/qr-code/getUnlimitedQRCode.html
        该接口用于获取小程序码，适用于需要的码数量极多的业务场景。通过该接口生成的小程序码，永久有效，数量暂无限制
        :return:
        """

        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        data = {
            "scene": scene,
            "path": path,
            "check_path": check_path,
            "env_version": env_version,
            "width": width,
            "auto_color": auto_color,
            "line_color": line_color,
            "is_hyaline": is_hyaline
        }
        path = "/wxa/getwxacodeunlimit"
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        try:
            response.json()
            return self.get_api_response_error_info(response)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return response.content

    def create_qr_code(self, path: str, width: int = 430, app_name: str = "doraemon") -> Union[dict, bytes]:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/qrcode-link/qr-code/createQRCode.html
        获取小程序二维码，适用于需要的码数量较少的业务场景。通过该接口生成的小程序码，永久有效，有数量限制
        """
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        data = {
            "path": path,
            "width": width
        }
        path = "/cgi-bin/wxaapp/createwxaqrcode"
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        try:
            response.json()
            return self.get_api_response_error_info(response)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return response.content

    def generate_scheme(
            self,
            jump_wxa: dict[str, str] = {"path": None, "query": None, "env_version": "release"},
            is_expire: bool = False,
            expire_time: int = int(time.time()) + (1 * 24 * 3600),
            expire_type: int = 0,
            expire_interval: int = 1,
            app_name: str = "doraemon"
    ) -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/qrcode-link/url-scheme/generateScheme.html
        用于获取小程序 scheme 码，适用于短信、邮件、外部网页、微信内等拉起小程序的业务场景。目前仅针对国内非个人主体的小程序开放
        """
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }

        data = {
            "jump_wxa": jump_wxa,
            "is_expire": is_expire,
            "expire_time": expire_time,
            "expire_type": expire_type,
            "expire_interval": expire_interval
        }
        path = "/wxa/generatescheme"
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def generate_url_link(
            self,
            path: str = None,
            query: dict = {},
            is_expire: bool = False,
            expire_type: int = 0,
            expire_time: int = int(time.time()) + (1 * 24 * 3600),
            expire_interval: int = 1,
            env_version: str = "release",
            app_name: str = "doraemon"
    ) -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/qrcode-link/url-link/generateUrlLink.html
        获取小程序 URL Link，适用于短信、邮件、网页、微信内等拉起小程序的业务场景。目前仅针对国内非个人主体的小程序开放
        """
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        if query:
            query = urlencode(query)
        data = {
            "path": path,
            "query": query,
            "is_expire": is_expire,
            "expire_type": expire_type,
            "expire_time": expire_time,
            "expire_interval": expire_interval,
            "env_version": env_version
        }
        path = "/wxa/generate_urllink"
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def generate_short_link(
            self,
            page_url: str,
            page_title: str = None,
            is_permanent: bool = False,
            app_name: str = "doraemon",
    ) -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/qrcode-link/short-link/generateShortLink.html
        获取小程序 Short Link，适用于微信内拉起小程序的业务场景。目前只开放给电商类目(具体包含以下一级类目：电商平台、商家自营、跨境电商)。
        通过该接口，可以选择生成到期失效和永久有效的小程序短链
        """
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        data = {
            "page_url": page_url,
            "page_title": page_title,
            "is_permanent": is_permanent
        }
        path = "/wxa/genwxashortlink"
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def get_temp_media(self, media_id: str, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/kf-mgnt/kf-message/getTempMedia.html
        该接口用于获取客服消息内的临时素材。即下载临时的多媒体文件。目前小程序仅支持下载图片文件
        """
        path = "/cgi-bin/media/get"
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token,
            "media_id": media_id
        }
        response = self.call_api("mini", app_name, "post", path, params=params)
        try:
            response.json()
            return self.get_api_response_error_info(response)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return response.content

    def set_typing(self, touser: str, command: str, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/kf-mgnt/kf-message/setTyping.html
        该接口用于下发客服当前输入状态给用户。
        """
        path = "/cgi-bin/message/custom/business/typing"
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        data = {
            "touser": touser,
            "command": command
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def upload_temp_media(self, type: str, media: "FormData", app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/kf-mgnt/kf-message/uploadTempMedia.html
        该接口用于把媒体文件上传到微信服务器。目前仅支持图片。用于发送客服消息或被动回复用户消息
        """
        path = "/cgi-bin/media/upload"
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token,
            "type": type
        }
        data = {
            "media": media
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def send_custom_message(self, touser: str, msgtype: str, app_name: str = "doraemon", **kwargs) -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/kf-mgnt/kf-message/sendCustomMessage.html
        该接口用于发送客服消息给用户

        :kwargs 参数如何传递详见文档链接
        """
        path = "/cgi-bin/message/custom/send"
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        data = {
            "touser": touser,
            "msgtype": msgtype,
            **kwargs
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def send_uniform_message(
            self, touser: str,
            weapp_template_msg: dict[str, Union[str, dict]],
            mp_template_msg: dict[str, str, Union[str, dict]],
            app_name: str = "doraemon"
    ) -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-message-management/uniform-message/sendUniformMessage.html
        该接口用于下发小程序和公众号统一的服务消息。

        weapp_template_msg 与 mp_template_msg 参数如何传递详见文档链接
        """
        path = "/cgi-bin/message/wxopen/template/uniform_send"
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        data = {
            "touser": touser,
            "weapp_template_msg": weapp_template_msg,
            "mp_template_msg": mp_template_msg
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def create_activity_id(self, unionid: str = None, openid: str = None, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-message-management/updatable-message/createActivityId.html
        该接口用于创建被分享动态消息或私密消息的 activity_id
        """
        path = "/cgi-bin/message/wxopen/activityid/create"
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        data = {
            "unionid": unionid,
            "openid": openid
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def set_updatable_msg(
            self,
            activity_id: str,
            target_state: int,
            template_info: dict[str, list[dict[str, str]]],
            app_name: str = "doraemon"
    ) -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-message-management/updatable-message/setUpdatableMsg.html
        该接口用于修改被分享的动态消息
        """
        path = "/cgi-bin/message/wxopen/updatablemsg/send"
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        data = {
            "activity_id": activity_id,
            "target_state": target_state,
            "template_info": template_info
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def delete_message_template(self, priTmplId: str, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-message-management/subscribe-message/deleteMessageTemplate.html
        该接口用于删除帐号下的个人模板
        """
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        path = "/wxaapi/newtmpl/deltemplate"
        data = {
            "priTmplId": priTmplId
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def get_category(self, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-message-management/subscribe-message/getCategory.html
        该接口用于获取小程序账号的类目
        """
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        path = "/wxaapi/newtmpl/getcategory"
        response = self.call_api("mini", app_name, "get", path, params=params)
        return self.get_response_info(response)

    def get_pub_template_key_words_by_id(self, tid: str, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-message-management/subscribe-message/getPubTemplateKeyWordsById.html
        该接口用于获取模板标题下的关键词列表
        """
        path = "/wxaapi/newtmpl/getpubtemplatekeywords"
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token,
            "tid": tid
        }
        response = self.call_api("mini", app_name, "get", path, params=params)
        return self.get_response_info(response)

    def get_pub_template_title_list(self, ids: str, start: str, limit: str, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-message-management/subscribe-message/getPubTemplateTitleList.html
        该接口用于获取帐号所属类目下的公共模板标题
        """
        path = "/wxaapi/newtmpl/getpubtemplatetitles"
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token,
            "ids": ids,
            "start": start,
            "limit": limit
        }
        response = self.call_api("mini", app_name, "get", path, params=params)
        return self.get_response_info(response)

    def get_message_template_list(self, app_name: str = "doraemon") -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-message-management/subscribe-message/getMessageTemplateList.html
        该接口用于获取当前帐号下的个人模板列表
        """
        path = "/wxaapi/newtmpl/gettemplate"
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        response = self.call_api("mini", app_name, "get", path, params=params)
        return self.get_response_info(response)

    def send_message(
            self,
            template_id: str,
            page: str,
            to_user: str,
            data: dict,
            mini_program_state: str,
            lang: str,
            app_name: str = "doraemon"
    ) -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-message-management/subscribe-message/sendMessage.html
        该接口用于发送订阅消息
        """
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        path = "/cgi-bin/message/subscribe/send"
        data = {
            "template_id": template_id,
            "page": page,
            "touser": to_user,
            "data": data,
            "miniprogram_state": mini_program_state,
            "lang": lang
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)

    def add_message_template(
            self,
            tid: str,
            kid_list: list[int],
            scene_desc: str = None,
            app_name: str = "doraemon"
    ) -> dict:
        """
        文档链接: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-message-management/subscribe-message/addMessageTemplate.html
        该接口用于组合模板并添加至帐号下的个人模板库
        """
        path = "/wxaapi/newtmpl/addtemplate"
        access_token = self.get_access_token(app_name)
        params = {
            "access_token": access_token
        }
        data = {
            "tid": tid,
            "kidList": kid_list,
            "sceneDesc": scene_desc
        }
        response = self.call_api("mini", app_name, "post", path, data=data, params=params)
        return self.get_response_info(response)
