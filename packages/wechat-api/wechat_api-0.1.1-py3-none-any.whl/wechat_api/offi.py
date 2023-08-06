import datetime
import json

from .base import WechatApi
from .models.base import Token
from .exceptions import ApiResponseError


class WechatOffiApi(WechatApi):
    tokens: dict[str, "Token"] = {}

    def get_access_token(self, app_name: str = "larrymao") -> str:
        token_info = self.tokens.get(app_name)

        if token_info and token_info.expires_on > datetime.datetime.now():
            return token_info.token

        app = self.tools.get_app("offi", app_name)
        path = "/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": app.app_id,
            "secret": app.secret_key,
        }

        response = self.call_api("offi", app_name, "get", path, params=params)
        result = response.json()

        if result.get('errcode') is not None:
            raise ApiResponseError("服务器接口响应失败", context={"response": response},
                                   error=self.get_api_response_error_info(response))

        self.tokens[app_name] = Token(
            token=result.get("access_token"),
            expires_on=datetime.datetime.now() + datetime.timedelta(seconds=int(result.get("expires_in", 0)))
        )
        return result.get("access_token")

    # def create_menu(self, menu: dict, app_name: str = "larrymao"):
    #     path = "/cgi-bin/menu/create"
    #     access_token = self.get_access_token()
    #     params = {
    #         "access_token": access_token
    #     }
    #     menu_json = json.dumps(menu, ensure_ascii=False).encode('utf-8')
    #     headers = {
    #         'encoding': 'utf-8'
    #     }
    #     response = self.call_api("offi", app_name, "post", path, params=params, headers=headers)
