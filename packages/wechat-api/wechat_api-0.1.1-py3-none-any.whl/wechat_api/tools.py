import time
import random
import base64
import datetime
from pathlib import Path
from typing import Any, Union, Optional, TYPE_CHECKING

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.asymmetric.types import PRIVATE_KEY_TYPES

from .models.base import TimedeltaParams
# from utils.logging import tracker, LogMsgFormatter

from .exceptions import DecryptError, AppImportError, LoadPrivateKeyError, GenerateSignatureError

if TYPE_CHECKING:
    from .models.state import WechatState, WechatApp


class WechatTools:
    __instance = None
    state: Optional["WechatState"] = None

    def __new__(cls, state: "WechatState"):
        if not cls.__instance:
            cls.state = state
            cls.__instance = object.__new__(cls)

        return cls.__instance

    @staticmethod
    def decrypt_aes(iv: str, key: str, data: str) -> bytes:
        """ 解密被 AES 加密的内容 """
        try:
            iv = base64.b64decode(iv)
            data = base64.b64decode(data)
            session_key = base64.b64decode(key)
            cipher = Cipher(AES(session_key), CBC(iv), default_backend())
            decryptor = cipher.decryptor()
            return decryptor.update(data) + decryptor.finalize()
        except Exception:
            # tracker.error(LogMsgFormatter(
            #     context={"iv": iv, "key": key, "data": data},
            #     action="通过微信库工具箱解密 AES 加密的内容",
            #     message="",
            #     traceback=traceback.format_exc()
            # ))
            raise DecryptError("服务器接口响应失败")

    @staticmethod
    def get_random_string(n=32) -> str:
        t = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
        return "".join(random.choices(t, k=n))

    @staticmethod
    def get_rfc3339_time(**kwargs: "TimedeltaParams") -> str:
        now = datetime.datetime.now() + datetime.timedelta(**kwargs)
        return f"{now.strftime('%Y-%m-%dT%H:%M:%S')}{time.strftime('%z')[:3]}:{time.strftime('%z')[3:]}"

    @staticmethod
    def format_private_key(private_key: str) -> str:
        """ 格式化 private_key """
        pem_start = "-----BEGIN PRIVATE KEY-----\n"
        pem_end = "\n-----END PRIVATE KEY-----"
        if not private_key.startswith(pem_start):
            private_key = pem_start + private_key
        if not private_key.endswith(pem_end):
            private_key = private_key + pem_end
        return private_key

    @classmethod
    def decrypt_pay_callback(cls, response_dict):
        nonce = response_dict.get("nonce")
        ciphertext = response_dict.get("ciphertext")
        associated_data = response_dict.get("associated_data")

        key_bytes = str.encode(cls.state.pay.v3_key)
        nonce_bytes = str.encode(nonce)
        ad_bytes = str.encode(associated_data)
        data = base64.b64decode(ciphertext)

        aesgcm = AESGCM(key_bytes)
        return aesgcm.decrypt(nonce_bytes, data, ad_bytes).decode("utf-8")

    @classmethod
    def load_private_key(cls, cert_path: Union["Path", str]) -> "PRIVATE_KEY_TYPES":
        """ 加载私钥 """
        try:
            with open(cert_path, "r") as f:
                private_key_str = f.read()
                return load_pem_private_key(
                    data=cls.format_private_key(private_key_str).encode("UTF-8"),
                    password=None,
                    backend=default_backend()
                )
        except Exception:
            # tracker.error(LogMsgFormatter(
            #     context={"cert_path": cert_path},
            #     action="通过微信库工具加载私钥",
            #     message=f"未能加载位于 {cert_path} 的私钥",
            #     traceback=traceback.format_exc()
            # ))
            raise LoadPrivateKeyError("服务器接口响应失败")

    @staticmethod
    def generate_rsa_sign(private_key: "PRIVATE_KEY_TYPES", sign_str: str) -> str:
        """ 生成 RSA 签名 """
        try:
            signature = private_key.sign(data=sign_str.encode("UTF-8"), padding=PKCS1v15(), algorithm=SHA256())
            sign = base64.b64encode(signature).decode("UTF-8").replace("\n", '')
            return sign
        except Exception:
            # tracker.error(LogMsgFormatter(
            #     context={"private_key": private_key, "sign_str": sign_str},
            #     action="通过微信库工具生成签名",
            #     message="",
            #     traceback=traceback.format_exc()
            # ))
            raise GenerateSignatureError("服务器接口响应失败")

    @classmethod
    def get_app(cls, package_name: str, app_name: str) -> "WechatApp":
        app = cls.state.get_app(package_name, app_name)

        if not app:
            # tracker.error(LogMsgFormatter(
            #     context={"package_name": package_name, "app_name": app_name},
            #     action="获取微信 App 配置信息",
            #     message=f"引入应用 {package_name}.{app_name} 不存在",
            # ))
            raise AppImportError("服务器接口响应失败")

        return app

    @staticmethod
    def get_utf8_str(data: Any) -> str:
        if isinstance(data, bytes):
            return data.decode("utf-8")
        if isinstance(data, str):
            return data

        return str(data)
