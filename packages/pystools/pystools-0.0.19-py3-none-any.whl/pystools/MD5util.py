import hashlib


class MD5Util:
    @staticmethod
    def md5_encode(*args, to_upper=False):
        m = hashlib.md5()
        # 将args中的所有值拼接起来
        for v in args:
            m.update(f"{v}".encode("utf-8"))
        if to_upper:
            return m.hexdigest().upper()
        return m.hexdigest()

