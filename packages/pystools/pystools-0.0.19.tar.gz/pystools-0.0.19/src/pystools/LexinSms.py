from MD5util import md5_encode


# 乐信短信接口
class LexinSms:
    def __init__(self, AppID, AppSecret, accName, accPwd):
        self.AppID = AppID
        self.AppSecret = AppSecret
        self.accName = accName
        self.accPwd = md5_encode(accPwd, to_upper=True)

    def send(self, aimcodes, content, msgId, extNo):
        accName = self.accName
        accPwd = self.accPwd
        url = f"http://sdk.lx198.com/sdk/send?dataType=json&accName={accName}&" \
              f"accPwd={accPwd}&aimcodes={aimcodes}&content={content}&msgId={msgId}&extNo={extNo}"
        """
        accName    用户名(乐信登录账号)
        aimcodes	手机号码(多个手机号码之间用英文半角“,”隔开,单次最多支持5000个号码)
        msgId	提交短信包的唯一id(15位以内数字)，推送短信回执时，会推送此值，用此值和手机号码来匹配短信的状态，如需要接受回执则必须提交此参数,单次提交只需要提交一个即可
        extNo	扩展号(6位以内数字)，推送短信上行时，会推送extNo，用extNo和手机号码来匹配短信的上行，单次提交只需要提交一个即可
        accPwd  密码(乐信登录密码32位MD5加密后转大写，如123456加密完以后为：E10ADC3949BA59ABBE56E057F20F883E)
        """

        # 使用urllib3库发送请求
        import urllib3
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        return r.data.decode('utf-8')

if __name__ == '__main__':
    AppID = "xxx"
    AppSecret = "xxx"
    accName = "xxx"
    accPwd = "xxx"
    aimcodes = "xxx"
    content = "验证码：1234，有效时间10分钟。如非本人操作，请忽略。【灵感涌现】"
    msgId = "12312312312"
    extNo = "123"
    sms = LexinSms(AppID, AppSecret, accName, accPwd)
    print(sms.send(aimcodes, content, msgId, extNo))
