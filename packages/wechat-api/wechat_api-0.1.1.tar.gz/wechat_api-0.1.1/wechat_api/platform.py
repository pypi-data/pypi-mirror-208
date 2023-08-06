import json

from .base import WechatApi
from .models.platform import PlatformAccessToken, PlatformUserInfo


class WechatPlatformApi(WechatApi):

    def decrypt(self, iv: str, key: str, data: str, app_name: str = "doraemon") -> str:
        """ 解密微信加密的内容

        文档：https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/signature.html
        """
        try:
            decrypt_data = self.tools.decrypt_aes(iv=iv, key=key, data=data)
            decrypt_data = decrypt_data[:-ord(decrypt_data[len(decrypt_data) - 1:])]
            decrypt_data = json.loads(decrypt_data)

            if decrypt_data['watermark']['appid'] != self.tools.get_app("offi", app_name).app_id:
                print("服务器接口响应失败")

            return decrypt_data
        except Exception:
            print("服务器接口响应失败")

    def get_access_token(self, code: str, app_name: str = "doraemon") -> PlatformAccessToken:
        """ 通过 code 获取 access_token """
        app = self.tools.get_app("platform", app_name)
        path = "/sns/oauth2/access_token"
        params = {
            "code": code,
            "appid": app.app_id,
            "secret": app.secret_key,
            "grant_type": "authorization_code",
        }

        response = self.call_api("platform", app_name, "get", path, params=params)

        return PlatformAccessToken(**response.json())

    def get_userinfo(self, access_token: str, openid: str, app_name: str = "doraemon"):
        path = "/sns/userinfo"
        params = {
            "openid": openid,
            "access_token": access_token,
        }

        response = self.call_api("platform", app_name, "get", path, params=params)

        return PlatformUserInfo(**response.json())
