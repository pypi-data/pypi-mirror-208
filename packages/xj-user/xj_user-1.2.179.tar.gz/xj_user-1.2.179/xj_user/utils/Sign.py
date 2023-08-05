import json
import string
import hashlib
import random
import time
import urllib
from main.settings import BASE_DIR
from django.core.cache import cache
from pathlib import Path
from ..utils.j_config import JConfig
from ..utils.j_dict import JDict
from ..utils.model_handle import parse_data, util_response

module_root = str(Path(__file__).resolve().parent)
# 配置之对象
main_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_payment"))
module_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_payment"))

appid = main_config_dict.wechat_subscription_app_id or module_config_dict.wechat_subscription_app_id or ""
sceret = main_config_dict.wechat_subscription_app_secret or module_config_dict.wechat_subscription_app_secret or ""


class Sign:

    def __init__(self, jsapi_ticket, url):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': self.__create_timestamp(),
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))  # 创建随机字符串

    def __create_timestamp(self):
        return int(time.time())  # 创建一个时间戳

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])  # 根据字符的ASCII值进行排序，拼接
        self.ret['signature'] = hashlib.sha1(string.encode('utf-8')).hexdigest()  # 对字符串进行sha1加密
        return self.ret


def get__token():
    ACCESS_TOKEN = cache.get('wx:ACCESS_TOKEN')  # 从redis中获取ACCESS_TOKEN
    if ACCESS_TOKEN:
        return ACCESS_TOKEN
    try:
        token_url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(
            appid, sceret)  # 创建获取token的url
        response = urllib.request.urlopen(token_url)
        b = response.read().decode('utf-8')
        token = json.loads(b)
        ACCESS_TOKEN = token.get("access_token")
        cache.set('wx:ACCESS_TOKEN', ACCESS_TOKEN, 7200)  # 将获取到的 ACCESS_TOKEN 存入redis中并且设置过期时间为7200s
        return ACCESS_TOKEN
    except Exception as e:
        return e


def get_ticket():
    ticket = cache.get('wx:ticket')  # 获取redis数据库中ticket
    if ticket:
        tic = str(ticket)
        return tic
    else:
        try:
            token = get__token()
            ticket_url = " https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={}&type=jsapi".format(token)
            get_ticket = urllib.request.urlopen(ticket_url)
            c = get_ticket.read().decode("utf-8")
            js_ticket = json.loads(c)
            ticket = js_ticket.get("ticket")
            cache.set('wx:ticket', ticket, 7200)
            return ticket
        except Exception as e:
            return e


def jssdk_config(url):
    ticket = get_ticket()
    sign = Sign(ticket, url)
    data = sign.sign()
    result = {
        "appId": appid,
        "nonceStr": data['nonceStr'],
        "jsapi_ticket": data['jsapi_ticket'],
        "timestamp": data['timestamp'],
        "url": data['url'],
        "signature": data['signature'],
    }
    return result
