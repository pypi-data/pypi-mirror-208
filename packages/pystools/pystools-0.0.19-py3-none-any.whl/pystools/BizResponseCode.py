from enum import Enum


class BizResponseCode(Enum):
    """
    - 系统级别 100xxx
    - 权限级别 200xxx
    - 逻辑级别 300xxx
    """
    SYSTEM_ERROR = 100000, "系统错误"
    TOKEN_INVALID = 200100, "token 过期或无效"
    NO_PERMISSION = 200001,"用户无权限"
    PARAM_ERROR = 300100, "参数错误"
    QUERY_NO_RESULT = 300200, "查询无结果"

    def __init__(self, code, desc):
        self._code = code
        self._desc = desc

    @property
    def desc(self):
        return self._desc

    @property
    def code(self):
        return self._code