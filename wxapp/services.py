import logging
import re
import time
from datetime import datetime, timedelta

from django.db.transaction import atomic
from wechatpy import WeChatComponent

from b2c.misc.models import Media
from b2c.users.models.merchant import Merchant
from b2c.users.models.merchant_config import MerchantConfig
from b2c.wxapp.filestorage import FileSessionStorage
from b2c.wxapp.models import WXOrderRefund, WXMchCert
from b2c.wxapp.models.wx_app_review_state_type import WXAppReviewStateType
from b2c.wxapp.models.wx_app_user import WXAppUser
from b2c.wxapp.models.wx_mch_cert_type import WXMchCertType
from b2c.wxapp.models.wx_mch_user import WXMchUser
from b2c.wxapp.models.wx_payment import WXPaymentOrder
from b2c.wxapp.models.wx_refund_state_type import WXRefundStateType
from b2c.wxapp.models.wx_trade_state_type import WXTradeStateType
from b2c.wxapp.wechat_api import *
from b2c.wxapp.wx_utils import *
from config.settings.base import WE_CHAT_APP

logger = logging.getLogger('django.server')

component = WeChatComponent(WE_CHAT_APP.get('APP_ID'), WE_CHAT_APP.get('APP_SECRET'),
                            WE_CHAT_APP.get('TOKEN'), WE_CHAT_APP.get('ENCODING_KEY'),
                            session=FileSessionStorage())


def wx_app_user_create(
        mch_user_id: str,
        open_id: str,
        **kwargs
) -> WXAppUser:
    """
    创建小程序用户
    :param mch_user_id:
    :param open_id:
    :return:
    """
    mch_user = WXMchUser.objects.filter(id=mch_user_id).first()
    app_user = WXAppUser(
        mch_user=mch_user,
        open_id=open_id,
    )
    for k, v in kwargs.items():
        if hasattr(app_user, k):
            setattr(app_user, k, v)
    app_user.clean()
    app_user.save()
    return app_user


def wx_app_user_update(
        app_user_id: int,
        mch_user_id: str,
        **kwargs
) -> WXAppUser:
    """
    更新小程序用户
    :param mch_user_id:
    :param app_user_id:
    :return:
    """
    app_user = WXAppUser.objects.filter(id=app_user_id, mch_user__id=mch_user_id).first()
    app_user.mch_user_id = mch_user_id
    for k, v in kwargs.items():
        if hasattr(app_user, k):
            setattr(app_user, k, v)
    app_user.clean()
    app_user.save()
    return app_user


def wx_mch_user_create_or_update(
        app_id: str,
        **kwargs
):
    """
    创建或更新商户
    :param app_id:
    :param kwargs:
    :return:
    """
    mch_user, _ = WXMchUser.objects.get_or_create(app_id=app_id)
    mch_user = wx_mch_user_update(mch_user.id, **kwargs)
    return mch_user


def wx_mch_user_create(
        app_id: str,
        mch_id: str,
        refresh_token: str,
        access_token: str = None,
        expires_in: int = 0,
        sign_key: str = None
) -> WXMchUser:
    """
    创建小程序商户
    :param refresh_token:
    :param sign_key:
    :param app_id:
    :param mch_id:
    :param access_token:
    :param expires_in:
    :return:
    """
    mch_user = WXMchUser(
        app_id=app_id,
        mch_id=mch_id,
        refresh_token=refresh_token,
        access_token=access_token,
        expires_in=expires_in,
        sign_key=sign_key
    )
    mch_user.clean()
    mch_user.save()
    return mch_user


def wx_mch_user_update(
        mch_user_id: str,
        **kwargs
) -> WXMchUser:
    """
    更新小程序商户信息

    :return:
    """
    mch_user = WXMchUser.objects.filter(id=mch_user_id).first()
    for k, v in kwargs.items():
        if hasattr(mch_user, k):
            setattr(mch_user, k, v)
    mch_user.clean()
    mch_user.save()
    return mch_user


def wx_app_user_create_or_update(mch_user_id, open_id, session_key, union_id=None):
    """
    用户更新或创建用户
    :param mch_user_id:
    :param open_id:
    :param session_key:
    :param union_id:
    :return:
    """
    app_user = WXAppUser.objects.filter(open_id=open_id).first()
    # TODO 维护token的生成方式
    token = get_str_md5(session_key)
    if app_user:
        app_user = wx_app_user_update(
            mch_user_id=mch_user_id, app_user_id=app_user.id, session_key=session_key,
            union_id=union_id, token=token)
    else:
        app_user = wx_app_user_create(
            mch_user_id=mch_user_id, open_id=open_id, session_key=session_key,
            union_id=union_id, token=token)
    return app_user


def wx_user_login_old(mch_user_id: int, code):
    """
    小程序用户登陆
    :param mch_user_id:
    :param code:
    :return:
    """

    logger.debug(f'mch_user_id---{mch_user_id}')
    logger.debug(f'login code---{code}')

    mch_user = WXMchUser.objects.filter(id=mch_user_id).first()
    auth = WXAppAuthUtils(mch_user.app_id, mch_user.app_secret)
    result = auth.login(code)
    if result:
        open_id, session_key = result
        return wx_app_user_create_or_update(mch_user_id, open_id, session_key)
    else:
        return None


def wx_user_login(mch_user_id: int, code):
    """
    小程序用户登陆
    :param mch_user_id:
    :param code:
    :return:
    """

    logger.debug(f'wx_user_login---{mch_user_id}---{code}')

    mch_user = WXMchUser.objects.filter(id=mch_user_id).first()
    auth = get_wx_3rd_auth_utils_by_mch_user(mch_user)
    result = auth.login(code)
    logger.debug(f'wx_user_login result---{result}')
    if 'session_key' in result.keys():
        open_id, session_key = result['openid'], result['session_key']
        return wx_app_user_create_or_update(mch_user_id, open_id, session_key)
    else:
        component.fetch_access_token()
        return wx_user_login(mch_user_id=mch_user_id, code=code)


def wx_order_create(
        app_user_id: int,
        mch_user_id: int,
        body: str,
        total_fee: int,
        notify_url: str,
        out_trade_no: str,
        client_ip: str,
        time_start: datetime,
        time_expire: datetime,
        trade_type: str = 'JSAPI',
) -> WXPaymentOrder:
    """
    创建小程序订单
    :param app_user_id:
    :param mch_user_id:
    :param trade_type:
    :param body:
    :param total_fee:
    :param notify_url:
    :param out_trade_no:
    :param client_ip:
    :param time_start:
    :param time_expire:
    :return:
    """

    app_user = WXAppUser.objects.filter(id=app_user_id).first()
    mch_user = WXMchUser.objects.filter(id=mch_user_id).first()
    wx_order = get_wx_order_utils_by_mch_user(mch_user)
    nonce_str = random_string(32)

    prepay_refresh_at = datetime.now()
    result_content = wx_order.create(
        nonce_str=nonce_str,
        trade_type=trade_type,
        body=body,
        total_fee=total_fee,
        notify_url=notify_url,
        out_trade_no=out_trade_no,
        client_ip=client_ip,
        time_start=time_start,
        time_expire=time_expire,
        user_id=app_user.open_id
    )
    logger.debug(f'wx_order_create---{out_trade_no}---{result_content}')

    return_code = result_content['return_code']
    return_msg = result_content['return_msg']
    result_code = result_content.get('result_code', '')
    err_code = result_content.get('err_code', '')
    err_code_des = result_content.get('err_code_des', '')
    prepay_id = result_content.get('prepay_id', '')
    code_url = result_content.get('code_url', '')

    wx_order = WXPaymentOrder.objects.filter(out_trade_no=out_trade_no).first()
    if wx_order:
        wx_order = _wx_order_update(wx_order.id, prepay_refresh_at=prepay_refresh_at, **result_content)
    else:
        wx_order = WXPaymentOrder(
            mch_user=mch_user,
            app_user=app_user,
            nonce_str=nonce_str,
            trade_type=trade_type,
            body=body,
            total_fee=total_fee,
            notify_url=notify_url,
            out_trade_no=out_trade_no,
            spbill_create_ip=client_ip,
            return_code=return_code,
            return_msg=return_msg,
            result_code=result_code,
            err_code=err_code,
            err_code_des=err_code_des,
            prepay_id=prepay_id,
            code_url=code_url,
            time_start=time_start,
            time_expire=time_expire,
            prepay_refresh_at=prepay_refresh_at
        )
        wx_order.save()
    return wx_order


def wx_order_is_trade_state(out_trade_no: str, state: WXTradeStateType):
    """
    判断交易状态是否为**
    :param out_trade_no:
    :param state:
    :return:
    """
    wx_order = WXPaymentOrder.objects.filter(out_trade_no=out_trade_no).first()
    if wx_order is None:
        return None
    if wx_order.is_success():
        return wx_order.trade_state and wx_order.trade_state == state


def parse_pay_notify(result_dict) -> WXPaymentOrder:
    """
    解析支付回调
    :param result_dict:
    :return:
    """

    logger.debug(f'parse_pay_notify---{result_dict}')

    out_trade_no = result_dict['out_trade_no']
    wx_order = WXPaymentOrder.objects.filter(out_trade_no=out_trade_no).first()
    if not wx_order:
        return None
    if 'SUCCESS' in result_dict['return_code'] and 'SUCCESS' in result_dict['result_code']:
        result_dict['trade_state'] = WXTradeStateType.SUCCESS.name
    return _wx_order_update(wx_order.id, **result_dict)


def parse_refund_notify(result_dict) -> WXPaymentOrder:
    """
    解析退款回调
    :param result_dict:
    :return:
    """
    logger.debug(f'parse_refund_notify---{result_dict}')
    return_code = result_dict['return_code']
    if not 'SUCCESS' == return_code:
        return None
    app_id = result_dict['appid']
    mch_id = result_dict['mch_id']
    nonce_str = result_dict['nonce_str']
    req_info = result_dict['req_info']

    wx_mch_user = WXMchUser.objects.get(app_id=app_id, mch_id=mch_id)
    decrypt_data = decrypt_wx_refund_data(wx_mch_user.sign_key, req_info)

    out_trade_no = decrypt_data['out_trade_no']
    wx_order = WXPaymentOrder.objects.filter(out_trade_no=out_trade_no).first()
    if not wx_order:
        return None
    update_data = decrypt_data
    update_data['app_id'] = app_id
    update_data['mch_id'] = mch_id
    update_data['nonce_str'] = nonce_str
    return _wx_order_refund_create_or_update(wx_order.id, **update_data)


def wx_order_trade_state_update(out_trade_no: str) -> WXPaymentOrder:
    """
    请求并更新交易状态
    :param out_trade_no:
    :return:
    """

    wx_order = WXPaymentOrder.objects.filter(out_trade_no=out_trade_no).first()
    wx_order_utils = get_wx_order_utils_by_mch_user(wx_order.mch_user)
    result_content = wx_order_utils.query(
        transaction_id=wx_order.transaction_id,
        out_trade_no=out_trade_no,
        nonce_str=wx_order.nonce_str)
    logger.debug(f'wx_order_trade_state_update---{out_trade_no}---{result_content}')
    return _wx_order_update(wx_order.id, **result_content)


def wx_order_close(out_trade_no: str) -> WXPaymentOrder:
    """
    关闭订单
    :param out_trade_no:
    :return:
    """

    wx_order = WXPaymentOrder.objects.filter(out_trade_no=out_trade_no).first()
    wx_order_utils = get_wx_order_utils_by_mch_user(wx_order.mch_user)
    result_content = wx_order_utils.close(
        out_trade_no=out_trade_no,
        nonce_str=wx_order.nonce_str)
    logger.debug(f'wx_order_close---{out_trade_no}---{result_content}')
    return _wx_order_update(wx_order.id, **result_content)


def wx_order_refund(out_trade_no: str, notify_url: str) -> WXPaymentOrder:
    """
    订单申请退款
    :param notify_url:
    :param out_trade_no:
    :return:
    """
    wx_order = WXPaymentOrder.objects.filter(out_trade_no=out_trade_no).first()
    wx_order_utils = get_wx_order_utils_by_mch_user(wx_order.mch_user)
    out_refund_no = f'r{out_trade_no}'
    result_content = wx_order_utils.refund_apply(
        total_fee=wx_order.total_fee, refund_fee=wx_order.total_fee, nonce_str=wx_order.nonce_str,
        out_trade_no=out_trade_no, out_refund_no=out_refund_no, notify_url=notify_url)
    result_content['notify_url'] = notify_url
    logger.debug(f'wx_order_refund---{out_trade_no}---{result_content}')
    return _wx_order_refund_create_or_update(wx_order.id, **result_content)


def wx_refund_trade_state_update(out_trade_no: str) -> WXPaymentOrder:
    """
    请求并更新退款状态
    :param out_trade_no:
    :return:
    """
    wx_order = WXPaymentOrder.objects.filter(out_trade_no=out_trade_no).first()
    wx_order_utils = get_wx_order_utils_by_mch_user(wx_order.mch_user)
    result_content = wx_order_utils.refund_query(
        out_trade_no=out_trade_no,
        nonce_str=wx_order.nonce_str)
    logger.debug(f'wx_refund_trade_state_update---{out_trade_no}---{result_content}')
    return _wx_order_refund_create_or_update(wx_order.id, **result_content)


@atomic
def _wx_order_refund_create_or_update(wx_order_id, **kwargs) -> WXPaymentOrder:
    """
    新建退款
    :param wx_order_id:
    :param kwargs:
    :return:
    """
    wx_order = WXPaymentOrder.objects.filter(id=wx_order_id).first()
    wx_refund = WXOrderRefund.objects.filter(wx_order=wx_order).first()
    if wx_refund is None:
        wx_refund = WXOrderRefund(wx_order=wx_order)
    for k, v in kwargs.items():
        match_refund = re.match('(.*)_\d+$', k)
        if match_refund:
            k = match_refund.group(1)
        if hasattr(wx_order, k):
            if 'trade_state' in k:
                v = WXTradeStateType[v].value
            setattr(wx_order, k, v)

        if hasattr(wx_refund, k):
            if 'refund_status' in k:
                v = WXRefundStateType[v].value
            if 'notify_url' not in k:
                setattr(wx_refund, k, v)

    wx_order.clean()
    wx_order.save()
    wx_refund.clean()
    wx_refund.save()
    return wx_order


def _wx_order_update(
        wx_order_id: int,
        **kwargs
) -> WXPaymentOrder:
    """
    更新用户订单信息
    :param wx_order_id:
    :return:
    """
    wx_order = WXPaymentOrder.objects.filter(id=wx_order_id).first()
    for k, v in kwargs.items():
        if hasattr(wx_order, k):
            if 'trade_state' in k:
                v = WXTradeStateType[v].value
            setattr(wx_order, k, v)
    wx_order.clean()
    wx_order.save()
    return wx_order


def refresh_wx_order(wx_order_id: int):
    """
    刷新订单prepay_id
    :param wx_order_id:
    :return:
    """
    # prepay_id 2小时失效需刷新 容错间隔200s
    prepay_id_expires = 7000
    wx_order = WXPaymentOrder.objects.filter(id=wx_order_id).first()
    if not wx_order:
        return None
    if (wx_order.prepay_refresh_at + timedelta(seconds=prepay_id_expires)) > datetime.now():
        return wx_order
    return wx_order_create(app_user_id=wx_order.app_user.id,
                           mch_user_id=wx_order.mch_user.id,
                           body=wx_order.body,
                           total_fee=wx_order.total_fee,
                           notify_url=wx_order.notify_url,
                           out_trade_no=wx_order.out_trade_no,
                           client_ip=wx_order.spbill_create_ip,
                           time_start=wx_order.time_start,
                           time_expire=wx_order.time_expire)


def get_wx_pay_params(wx_order_id: int, sign_type='MD5'):
    """
    获取小程序支付相关参数(返回给小程序调用支付)
    :param wx_order_id:
    :param sign_type:
    :return:
    """
    wx_order = refresh_wx_order(wx_order_id)
    if wx_order is None:
        return None
    data = {
        'appId': wx_order.mch_user.app_id,
        'timeStamp': str(int(time.time())),
        'nonceStr': wx_order.nonce_str,
        'package': 'prepay_id={}'.format(wx_order.prepay_id),
        'signType': sign_type,
    }
    sign = calc_sign(data, wx_order.mch_user.sign_key)
    data['paySign'] = sign
    data.pop('appId')
    return data


def wx_user_info_decrypt(token, mch_user_id, encrypted_data, iv):
    """
    小程序用户信息解密并保存
    :param token:
    :param mch_user_id:
    :param encrypted_data:
    :param iv:
    :return:
    """
    app_user = WXAppUser.objects.filter(mch_user__id=mch_user_id, token=token).first()
    if app_user:
        real_data = wx_data_decrypt(app_user.mch_user.app_id, app_user.session_key, encrypted_data, iv)
        app_user = wx_app_user_update(
            app_user_id=app_user.id,
            mch_user_id=mch_user_id,
            nick_name=real_data['nickName'],
            gender=real_data['gender'],
            city=real_data['city'],
            province=real_data['province'],
            country=real_data['country'],
            avatarUrl=real_data['avatarUrl'],
            unionId=real_data.get('unionId')
        )
    return app_user


def wx_user_phone_decrypt(token, mch_user_id, encrypted_data, iv):
    """
    小程序手机号解密并保存
    :param token:
    :param mch_user_id:
    :param encrypted_data:
    :param iv:
    :return:
    """
    app_user = WXAppUser.objects.filter(mch_user__id=mch_user_id, token=token).first()
    if app_user:
        real_data = wx_data_decrypt(app_user.mch_user.app_id, app_user.session_key, encrypted_data, iv)
        country_code = real_data['countryCode']
        phone_number = real_data['phoneNumber']
        pure_phone_number = real_data['purePhoneNumber']
        app_user = wx_app_user_update(
            app_user_id=app_user.id,
            mch_user_id=mch_user_id,
            country_code=country_code,
            phone_number=phone_number,
            pure_phone_number=pure_phone_number)
    return app_user


def wx_data_decrypt(app_id, session_key, encrypted_data, iv):
    """
    小程序用户数据解密
    :param app_id:
    :param session_key:
    :param encrypted_data:
    :param iv:
    :return:
    """
    wc_crypt = WXBizDataCrypt(app_id, session_key)
    real_data = wc_crypt.decrypt(encrypted_data, iv)
    return real_data


def get_wx_order_utils_by_mch_user(mch_user: WXMchUser) -> WXOrderUtils:
    """
    根据mch_user获取order工具
    :param mch_user:
    :return:
    """

    logger.debug(f'get_wx_order_utils_by_mch_user---{mch_user.id}---{mch_user.cert_pem_file}---{mch_user.key_pem_file}')
    wx_utils = WXOrderUtils(
        app_id=mch_user.app_id,
        mch_id=mch_user.mch_id,
        sign_key=mch_user.sign_key,
        cert_path=(mch_user.cert_pem_file,
                   mch_user.key_pem_file)
    )
    return wx_utils


def get_wx_3rd_auth_utils_by_mch_user(mch_user) -> WX3rdAppAuthUtils:
    """
    根据mch_user获取order工具
    :param mch_user:
    :return:
    """
    return WX3rdAppAuthUtils(
        component_appid=component.component_appid,
        component_access_token=component.access_token,
        authorizer_appid=mch_user.app_id,
        authorizer_refresh_token=mch_user.refresh_token
    )


def get_access_token(mch_user_id: int, refresh: bool = False):
    """
    获取商户access_token
    :param mch_user_id:
    :param refresh:
    :return:
    """
    mch_user = WXMchUser.objects.get(id=mch_user_id)
    access_token = mch_user.access_token
    expires_in = mch_user.expires_in
    token_refresh_at = mch_user.token_refresh_at
    if refresh or (access_token is None) or ((token_refresh_at + timedelta(seconds=expires_in)) < datetime.now()):
        access_token = _refresh_access_token(mch_user_id).access_token
    return access_token


def _refresh_access_token(mch_user_id: int):
    """
    刷新商户access_token
    :param mch_user_id:
    :return:
    """
    mch_user = WXMchUser.objects.get(id=mch_user_id)
    auth = get_wx_3rd_auth_utils_by_mch_user(mch_user)
    result = auth.get_authorizer_access_token()
    logger.debug(f'_refresh_access_token---{result}')
    if 'authorizer_access_token' in result.keys():
        authorizer_access_token = result['authorizer_access_token']
        expires_in = result['expires_in']
        authorizer_refresh_token = result['authorizer_refresh_token']
        mch_user.access_token = authorizer_access_token
        mch_user.expires_in = expires_in
        mch_user.refresh_token = authorizer_refresh_token
        mch_user.token_refresh_at = datetime.now()
        mch_user.save()
    return mch_user


def get_wxa_code(
        mch_user_id: int,
        wxa_path,
        scene='wxapp',
        width=430,
        auto_color=False,
        line_color=None,
        is_hyaline=True,
        refresh: bool = False
):
    """
    根据路径获取小程序码
    """
    access_token = get_access_token(mch_user_id, refresh)
    kwargs = {'access_token': access_token,
              'wxa_path': wxa_path,
              'scene': scene,
              'width': width,
              'auto_color': auto_color,
              'line_color': line_color,
              'is_hyaline': is_hyaline}

    content, is_image = get_wxa_code_image(**kwargs)
    if not is_image:
        logger.debug(f'get_wxa_code error ---{content}')
        access_token = get_access_token(mch_user_id, True)
        kwargs['access_token'] = access_token
        content, is_image = get_wxa_code_image(**kwargs)
    return content, is_image


@atomic
def update_mch_user_cert(wx_mch_user_id, mch_id, sign_key, cert_pem_uuid, key_pem_uuid):
    """
    更新小程序商户证书
    :param wx_mch_user_id:
    :param mch_id:
    :param sign_key:
    :param cert_pem_uuid:
    :param key_pem_uuid:
    :return:
    """
    wx_mch_user_update(wx_mch_user_id, mch_id=mch_id, sign_key=sign_key)
    update_mch_user_cert_by_type(wx_mch_user_id, WXMchCertType.CERT_PEM, cert_pem_uuid)
    update_mch_user_cert_by_type(wx_mch_user_id, WXMchCertType.KEY_PEM, key_pem_uuid)


@atomic
def update_mch_user_cert_by_type(wx_mch_user_id, cert_type: WXMchCertType, uuid):
    """
    更新商户证书
    :return:
    """
    mch_user = WXMchUser.objects.get(id=wx_mch_user_id)
    mch_cert, _ = WXMchCert.objects.get_or_create(mch_user=mch_user, cert_type=cert_type.value)
    if cert_type == WXMchCertType.CERT_PEM:
        old_cert = mch_user.cert_pem
    elif cert_type == WXMchCertType.KEY_PEM:
        old_cert = mch_user.key_pem
    else:
        return None
    media = Media.objects.get(uuid=uuid)
    media.content_object = mch_cert
    media.expired_at = None
    media.order = 0
    media.save()
    if old_cert and str(old_cert.uuid) != uuid:
        old_cert.delete()
    return mch_user


def get_wx_payment_no(out_trade_no: int):
    """
    根据商户订单号获取微信支付订单号
    :param out_trade_no:
    :return:
    """
    wx_order = WXPaymentOrder.objects.filter(out_trade_no=out_trade_no).first()
    return wx_order.transaction_id if wx_order else None


def get_wx_refund_no(out_trade_no: int):
    """
    根据商户订单号获取微信退款单号
    :param out_trade_no:
    :return:
    """
    wx_order = WXPaymentOrder.objects.filter(out_trade_no=out_trade_no).first()
    return wx_order.refund.refund_id if wx_order and wx_order.refund else None


def poll_audit_status():
    """
    查询小程序商户的审核状态
    :return:
    """
    logger.debug('************ poll_audit_status start ************')
    wx_mch_users = WXMchUser.objects.filter(app_review_status=WXAppReviewStateType.PROCESSING.value)
    for user in wx_mch_users:
        status, result = last_audit_status(get_access_token(user.id))
        if status == WXAppReviewStateType.SUCCESS.value:
            review_status = WXAppReviewStateType.SUCCESS.value
        elif status == WXAppReviewStateType.PROCESSING.value:
            review_status = WXAppReviewStateType.PROCESSING.value
        else:
            review_status = WXAppReviewStateType.FAILED.value
        wx_mch_user_create_or_update(app_id=user.app_id, app_review_status=review_status,
                                     app_review_result=result, app_reviewed_at=datetime.now())
        if status == WXAppReviewStateType.SUCCESS.value:
            release(get_access_token(user.id))
    logger.debug('************ poll_audit_status end ************')


def submit_audit_all_merchant():
    """
    用最新模板提交小程序商户
    :return:
    """
    wx_mch_users = WXMchUser.objects.all()
    for user in wx_mch_users:
        if not (user.app_review_status == WXAppReviewStateType.FAILED.value):
            # 小程序提交模板代码
            result, templates = template_list(str(component.access_token))
            if len(templates):
                config = MerchantConfig.objects.filter(wx_mch_user=user).first()
                if config:
                    merchant = config.merchant
                    template = templates[len(templates) - 1]
                    f = open('b2c/wxapp/config/app.json', 'r')
                    ext_str = f.read()
                    ext_json = json.loads(ext_str)
                    ext_json['ext']['name_code'] = merchant.name_code
                    ext_json['ext']['title'] = merchant.name
                    access_token = get_access_token(user.id)
                    commit_code(access_token, template['template_id'], json.dumps(ext_json), template['user_version'],
                                template['user_desc'])
                    # 小程序提交审核
                    if user.app_review_status == WXAppReviewStateType.PROCESSING.value:
                        if not (user.app_version == template['user_version']):
                            undocodeaudit(access_token)
                    status_code, result = submit_audit(access_token=access_token, category_list=None)
                    if status_code:
                        wx_mch_user_create_or_update(app_id=user.app_id,
                                                     app_review_status=WXAppReviewStateType.PROCESSING.value,
                                                     app_version=template['user_version'],
                                                     app_submitted_at=datetime.now())
