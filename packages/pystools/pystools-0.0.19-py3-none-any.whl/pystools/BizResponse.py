import datetime
from typing import Any
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, Dict, Optional, Sequence, Type

from .BizResponseCode import BizResponseCode


class BizException(Exception):
    def __init__(self, resp_code: Any, msg: str, data: Any = {}):
        if isinstance(resp_code, BizResponseCode):
            self.code = resp_code.code
        else:
            self.code = resp_code
        self.msg = msg
        self.data = data

class BizResponse:
    def __init__(self, data: Any, code: int = 0, msg: str = "success"):

        # 遍历data到最底层，如果字段类型是datetieme
        data = convert_datetime(data)

        self.code = code
        self.msg = msg
        self.data = data


def convert_datetime(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, datetime.datetime):
                # 转换为字符串，格式为：2020-01-01 00:00:00
                data[k] = v.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(v, list):
                for i in v:
                    if isinstance(i, datetime.datetime):
                        i = i.strftime("%Y-%m-%d %H:%M:%S")
                    elif isinstance(i, dict):
                        convert_datetime(i)
            elif isinstance(v, dict):
                convert_datetime(v)
    return data

