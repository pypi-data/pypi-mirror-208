from fastapi import Header

# from src.pystools.Jwt import Jwt
from .Jwt import Jwt


class FastapiAuthToken:
    def __init__(self, exp_seconds=60 * 60 * 6, secret_key="ca42ce27b859f6b361a718877aac6872", ):
        self.secret_key = secret_key
        self.exp_seconds = exp_seconds

    def generate_token(self, payload_data, **kwargs):
        return Jwt.generate_token(payload_data, self.exp_seconds, self.secret_key, kwargs)

    # 定义一个依赖函数，用来验证token并返回用户信息
    def validate_token(self, astoken: str = Header(...)):
        key = self.secret_key
        return Jwt.validate_token(astoken, key)
