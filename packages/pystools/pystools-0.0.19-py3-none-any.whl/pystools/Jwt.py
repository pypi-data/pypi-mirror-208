from authlib.jose import jwt, JoseError
import time

from .BizResponse import BizException
from .BizResponseCode import BizResponseCode


class Jwt:

    @staticmethod
    def generate_token(payload_data, exp_seconds=60 * 60 * 6, secret_key="ca42ce27b859f6b361a718877aac6872", **kwargs):
        """生成用于验证的JWT（json web token）"""
        # 签名算法
        header = {'alg': 'HS256'}
        # 用于签名的密钥
        key = secret_key
        # 待签名的数据负载
        # payload = {"exp":60*30}
        payload = {"exp": int(time.time()) + exp_seconds}
        """
        | 字段 | 说明 |
        | --- | --- |
        | iss | (issuer)：签发人 |
        | exp | (expiration time)：过期时间 |
        | sub | (subject)：主题 |
        | aud | (audience)：受众 |
        | nbf | (Not Before)：生效时间 |
        | iat | (Issued At)：签发时间 |
        | jti | (JWT ID)：编号 |
        """

        data = {**payload_data, **kwargs, **payload}

        return jwt.encode(header=header, payload=data, key=key)

    # 定义一个依赖函数，用来验证token并返回用户信息
    @staticmethod
    def validate_token(astoken: str, secret_key="ca42ce27b859f6b361a718877aac6872", ):
        key = secret_key
        try:
            # 解码token，如果过期或无效会抛出异常
            data = jwt.decode(astoken, key)
            data.validate_exp(now=int(time.time()), leeway=0)
            # 返回信息
            return data
        except JoseError:
            raise BizException(BizResponseCode.TOKEN_INVALID.code, "登录状态过期或无效")
