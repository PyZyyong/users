import base64
import hashlib
import json
import random
import socket
import string
from xml.etree import ElementTree

import requests
from Crypto.Cipher import AES

wx_api_url_base = 'https://api.weixin.qq.com'
# 用户登录认证
wx_auth_url_jscode2session = wx_api_url_base + '/sns/jscode2session'
# 用户access_token获取
wx_auth_url_access_token = wx_api_url_base + '/cgi-bin/token'
# 小程序码生成
wx_app_url_qr_code = wx_api_url_base + '/wxa/getwxacodeunlimit'

# 3rd用户登录认证
wx_auth_url_component_jscode2session = wx_api_url_base + '/sns/component/jscode2session'
# 3rd用户access_token获取
wx_auth_url_authorizer_access_token = wx_api_url_base + '/cgi-bin/component/api_authorizer_token'

wx_mch_url_base = 'https://api.mch.weixin.qq.com'
# 统一下单
wx_mch_url_unified_order = wx_mch_url_base + '/pay/unifiedorder'
# 查询订单
wx_mch_url_order_query = wx_mch_url_base + '/pay/orderquery'
# 关闭订单
wx_mch_url_close_order = wx_mch_url_base + '/pay/closeorder'
# 申请退款
wx_mch_url_pay_refund = wx_mch_url_base + '/secapi/pay/refund'
# 查询退款
wx_mch_url_refund_query = wx_mch_url_base + '/pay/refundquery'


class WXAppBase:
    _client = requests
    _timeout = 15

    def get(self, url, **kwargs):
        kwargs['timeout'] = self._timeout
        return self._client.get(url, **kwargs)

    def post(self, url, **kwargs):
        kwargs['timeout'] = self._timeout
        return self._client.post(url, **kwargs)


class WXAppAuthUtils(WXAppBase):

    def __init__(self, appid, appsecret):
        self.appid = appid
        self.appsecret = appsecret

    def login(self, code):
        params = {
            'appid': self.appid,
            'secret': self.appsecret,
            'js_code': code,
            'grant_type': 'authorization_code',
        }

        rep = self.get(url=wx_auth_url_jscode2session, params=params)
        rep_data = json.loads(rep.text)
        if 'session_key' in rep_data.keys():
            return rep_data['openid'], rep_data['session_key']
        return None

    def get_access_token(self):
        params = {
            'grant_type': 'client_credential',
            'appid': self.appid,
            'secret': self.appsecret
        }
        rep = self.get(url=wx_auth_url_access_token, params=params)
        rep_data = json.loads(rep.text)
        if 'access_token' in rep_data.keys():
            return rep_data['access_token'], rep_data['expires_in']
        return None


class WX3rdAppAuthUtils(WXAppBase):

    def __init__(self, component_appid, component_access_token, authorizer_appid, authorizer_refresh_token):
        self.component_appid = component_appid
        self.component_access_token = component_access_token
        self.authorizer_appid = authorizer_appid
        self.authorizer_refresh_token = authorizer_refresh_token

    def login(self, code):
        params = {
            'appid': self.authorizer_appid,
            'js_code': code,
            'grant_type': 'authorization_code',
            'component_appid': self.component_appid,
            'component_access_token': self.component_access_token
        }

        return self.get(url=wx_auth_url_component_jscode2session, params=params)

    def get_authorizer_access_token(self):
        params = {
            'component_access_token': self.component_access_token
        }
        data = {
            'component_appid': self.component_appid,
            'authorizer_appid': self.authorizer_appid,
            'authorizer_refresh_token': self.authorizer_refresh_token,
        }
        return self.post(url=wx_auth_url_authorizer_access_token, params=params, data=json.dumps(data))

    def get(self, url, **kwargs):
        rep_data = super(WX3rdAppAuthUtils, self).get(url, **kwargs)
        return json.loads(rep_data.text)

    def post(self, url, **kwargs):
        rep_data = super(WX3rdAppAuthUtils, self).post(url, **kwargs)
        return json.loads(rep_data.text)


class WXOrderUtils(WXAppBase):
    TRADE_TYPE = 'JSAPI'
    SIGN_TYPE = 'MD5'
    FEE_TYPE = 'CNY'

    def __init__(self, app_id, mch_id, sign_key, cert_path=None):
        self.app_id = app_id
        self.mch_id = mch_id
        self.sign_key = sign_key
        self.cert_path = cert_path

    def create(self, nonce_str, body,
               total_fee, notify_url, out_trade_no, client_ip, time_start, time_expire,
               user_id, detail=None, attach=None, trade_type=TRADE_TYPE, fee_type=FEE_TYPE, goods_tag=None,
               product_id=None, device_info=None, sign_type=SIGN_TYPE, limit_pay=None):
        time_start = time_start.strftime('%Y%m%d%H%M%S')
        time_expire = time_expire.strftime('%Y%m%d%H%M%S')
        body = body
        data = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': nonce_str,
            'body': body,
            'out_trade_no': out_trade_no,
            'total_fee': total_fee,
            'spbill_create_ip': client_ip or get_external_ip(),
            'notify_url': notify_url,
            'trade_type': trade_type,
            'device_info': device_info,
            'sign_type': sign_type,
            'detail': detail,
            'attach': attach,
            'fee_type': fee_type,
            'time_start': time_start,
            'time_expire': time_expire,
            'goods_tag': goods_tag,
            'product_id': product_id,
            'limit_pay': limit_pay,
            'openid': user_id,
        }
        return self.post(wx_mch_url_unified_order, data=data)

    def query(self, transaction_id, out_trade_no, nonce_str, sign_type=SIGN_TYPE):
        data = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'transaction_id': transaction_id,
            'out_trade_no': out_trade_no,
            'nonce_str': nonce_str,
            'sign_type': sign_type,
        }

        return self.post(wx_mch_url_order_query, data=data)

    def close(self, out_trade_no, nonce_str, sign_type=SIGN_TYPE):
        data = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'out_trade_no': out_trade_no,
            'nonce_str': nonce_str,
            'sign_type': sign_type,
        }
        return self.post(wx_mch_url_close_order, data=data)

    def refund_apply(
            self, total_fee, refund_fee, out_refund_no, nonce_str,
            out_trade_no, notify_url, fee_type='CNY', op_user_id=None,
            refund_account='REFUND_SOURCE_UNSETTLED_FUNDS'):
        data = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': nonce_str,
            'out_trade_no': out_trade_no,
            'out_refund_no': out_refund_no,
            'total_fee': total_fee,
            'refund_fee': refund_fee,
            'refund_fee_type': fee_type,
            'op_user_id': op_user_id if op_user_id else self.mch_id,
            'refund_account': refund_account,
            'notify_url': notify_url,
        }
        return self.post(wx_mch_url_pay_refund, data=data, cert=self.cert_path)

    def refund_query(self, nonce_str, out_trade_no):
        data = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': nonce_str,
            'out_trade_no': out_trade_no,
        }
        return self.post(wx_mch_url_refund_query, data=data)

    def post(self, url, **kwargs):
        data = kwargs['data']
        data = {k: v for k, v in data.items() if v is not None}
        sign = calc_sign(data, self.sign_key)
        data['sign'] = sign
        kwargs['data'] = dict_to_xml(data).encode('utf-8')
        rep = super(WXOrderUtils, self).post(url, **kwargs)
        return xml_to_dict(rep.content)


class WXBizDataCrypt:
    def __init__(self, app_id, session_key):
        self.appId = app_id
        self.sessionKey = session_key

    def decrypt(self, encrypted_data, iv):
        session_key = base64.b64decode(self.sessionKey)
        encrypted_data = base64.b64decode(encrypted_data)
        iv = base64.b64decode(iv)

        cipher = AES.new(session_key, AES.MODE_CBC, iv)

        decrypted = json.loads(self._un_pad(cipher.decrypt(encrypted_data)))

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    @staticmethod
    def _un_pad(s):
        return s[:-ord(s[len(s) - 1:])]


def get_wxa_code_image(
        access_token,
        wxa_path,
        scene='wxapp',
        width=430,
        auto_color=False,
        line_color=None,
        is_hyaline=True
):
    if line_color is None:
        line_color = {'r': '0', 'g': '0', 'b': '0'}
    url = wx_app_url_qr_code
    params = {'access_token': access_token}
    data = {
        'scene': scene,
        'page': wxa_path,
        'width': width,
        'auto_color': auto_color,
        'line_color': line_color,
        'is_hyaline': is_hyaline,
    }
    rep = requests.post(url, params=params, data=json.dumps(data))
    is_image = 'image' in rep.headers['Content-Type']
    return rep.content, is_image


def get_external_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        wechat_ip = socket.gethostbyname('api.mch.weixin.qq.com')
        sock.connect((wechat_ip, 80))
        addr, port = sock.getsockname()
        sock.close()
        return addr
    except socket.error:
        return '127.0.0.1'


def decrypt_wx_refund_data(sign_key, encrypt_data):
    """
    解密微信退款数据
    :param sign_key:
    :param encrypt_data:
    :return:
    """

    def un_pad(s):
        return s[:-ord(s[len(s) - 1:])]

    sign_key_md5 = get_str_md5(sign_key, upper=False).encode('utf-8')
    encrypt_data_64 = base64.b64decode(encrypt_data)
    aes = AES.new(sign_key_md5, AES.MODE_ECB)
    decrypted_text = aes.decrypt(encrypt_data_64)
    return xml_to_dict(un_pad(decrypted_text))


def calc_sign(params, sign_key):
    """
    微信计算签名
    :param params:
    :param sign_key:
    :return:
    """
    sign_data = ['{0}={1}'.format(k, params[k]) for k in sorted(params) if params[k]]
    sign_data.append('key={0}'.format(sign_key))
    sign_data = '&'.join(sign_data)
    md5_sign_data = get_str_md5(sign_data)
    return md5_sign_data


def random_string(length=16):
    """
    随机字符串
    :param length:
    :return:
    """
    rule = string.ascii_letters + string.digits
    rand_list = random.sample(rule, length)
    return ''.join(rand_list)


def get_str_md5(temp, upper: bool = True):
    """
    获取字符串md5
    :param temp:
    :param upper:
    :return:
    """
    md5_str = hashlib.md5(temp.encode('utf-8')).hexdigest()
    return md5_str.upper() if upper else md5_str.lower()


def dict_to_xml(dict_data):
    """
    dict 转为 xml
    :param dict_data:
    :return:
    """
    xml = ["<xml>"]
    for k, v in dict_data.items():
        xml.append("<{0}>{1}</{0}>".format(k, v))
    xml.append("</xml>")
    return "".join(xml)


def xml_to_dict(xml_data):
    """
    xml 转为 dict
    :param xml_data:
    :return:
    """
    xml_dict = {}
    root = ElementTree.fromstring(xml_data)
    for child in root:
        xml_dict[child.tag] = child.text
    return xml_dict
