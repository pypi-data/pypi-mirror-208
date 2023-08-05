# 绑定秀米账号
import hashlib
import json
import random
import time

import urllib3

from .Feishu import Feishu

http = urllib3.PoolManager()


class Xiumi(object):
    def __init__(self, appid, secret):
        self.appid = appid
        self.secret = secret

    def partner_bind(self, partner_user_id):
        """
        绑定秀米账号
        https://ent.xiumi.us/doc2.html
        :param partner_user_id:  用户在平台（不是秀米）的唯一ID。 可以不使用平台的用户编号，而为秀米对接特地生成一个专用的ID字符串。建议是飞书的user ID
        :return:
        """
        timestamp = int(time.time())  # 1544426764   当前UNIX时间戳，单位：秒。需不早于当前时间5分钟。
        nonce = random.randint(100000, 999999)  # 随机字符串，由您的平台在每一次签名时生成，使用于签名算法内。如 590946
        partner_user_id = partner_user_id  # 用户在平台（不是秀米）的唯一ID。 可以不使用平台的用户编号，而为秀米对接特地生成一个专用的ID字符串。
        data = [str(partner_user_id), str(self.secret), str(timestamp), str(nonce)]
        data.sort()
        cs = "".join(data)
        signature = hashlib.md5(cs.encode(encoding='UTF-8')).hexdigest()
        signature = hashlib.md5(signature.encode(encoding='UTF-8')).hexdigest()
        url = "https://xiumi.us/auth/partner/bind?signature={}&timestamp={}&nonce={}&partner_user_id={}&appid={}".format(
            signature, timestamp, nonce, partner_user_id, self.appid
        )
        return url

    def feishu_bot_bind_user(self, message, sender, feishu: Feishu):
        # print('+++++++++++++', message)

        bot_openid = feishu.bot_info().get('open_id')

        sender_id = sender.get("sender_id", {})
        user_id = sender_id.get("user_id", str(random.randint(100000, 999999)))
        # message = event.get("message", {})
        message_type = message.get("message_type", "")
        chat_type = message.get("chat_type", "")
        chat_id = message.get("chat_id", "")
        mentions = message.get("mentions", [])
        msg_text = ''
        if "text" in message_type:
            content = message.get("content", "")
            content_json = json.loads(content)
            msg_text = content_json.get("text", "")

        # 如果收到 绑定秀米 就回复绑定链接
        msg_type = "text"
        receive_id_type = ""
        receive_id = ""
        is_mention_bot = False
        bot_name = '机器人'
        if "p2p" in chat_type:
            receive_id_type = "user_id"
            receive_id = user_id
        elif "group" in chat_type:
            receive_id_type = "chat_id"
            receive_id = chat_id
            if mentions:
                mention_openids = []
                for mention in mentions:
                    ids = mention.get("id", {})
                    # print('================',mention)

                    bot_name = mention.get("name", '机器人')
                    mention_openids.append(ids.get("open_id"))
                # 如果提到了机器人
                if bot_openid in mention_openids:
                    is_mention_bot = True
        # print('================bot_openid', bot_openid)
        # print('================is_mention_bot', is_mention_bot)
        # print('================msg_text', msg_text)
        send_cmd = False
        bind_url = self.partner_bind(user_id)
        text = "您的专属绑定链接已生成，请在【五分钟内】使用，过期失效\n" \
               "1、请先在默认浏览器中登录您的秀米账号\n" \
               "2、点击以下链接，确认在登录秀米账号的浏览器中打开\n" \
               "{} \n\n 如需解绑，请回复【解绑秀米账号】并@{}".format(bind_url, bot_name)
        if "解绑秀米" in msg_text:
            text = "1、请先在默认浏览器中登录您的秀米账号\n" \
                   "2、点击以下链接，确认在登录秀米账号的浏览器中打开\n" \
                   "3、点击链接，进入解绑页面 https://xiumi.us/#/user/partnerbind " \
                   "\n\n 如需绑带秀米账号，请回复【绑定秀米账号】并@{}".format(bot_name)
            if "p2p" in chat_type:
                send_cmd = True
            elif is_mention_bot:
                send_cmd = True
                text = "<at user_id=\"{}\">Tom</at> {}".format(user_id, text)

        if "绑定秀米" in msg_text:
            if "p2p" in chat_type:
                send_cmd = True
            elif is_mention_bot:
                send_cmd = True
                text = "<at user_id=\"{}\">Tom</at> {}".format(user_id, text)

        content = json.dumps({"text": text}, ensure_ascii=False)
        resp_data = {
            'to_send': send_cmd,
            "receive_id_type": receive_id_type,
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": content
        }

        return resp_data


if __name__ == '__main__':
    appid = "xxxxx"
    secret = "xxxx"
    exec = Xiumi(appid, secret)
    print(exec.partner_bind("123"))
