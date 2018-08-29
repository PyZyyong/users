import json
import logging
from datetime import datetime

import coreapi
import coreschema
import requests
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from wechatpy.session.memorystorage import MemoryStorage

from b2c.general.helpers import get_merchant_from_merchant_user
from b2c.general.mixins import SimpleCodenamePermissionMixin
from b2c.users.models import MerchantConfig
from b2c.users.models.merchant import Merchant
from b2c.users.permissions import IsMerchantUserPermission
from b2c.users.services import update_merchant_config, cancel_authorize
from b2c.wxapp import wechat_api
from b2c.wxapp.services import component
from b2c.wxapp.models.wx_app_review_state_type import WXAppReviewStateType
from b2c.wxapp.services import wx_mch_user_create_or_update, get_access_token, submit_audit_all_merchant
from config.settings.base import WE_CHAT_APP

logger = logging.getLogger('django')
memorystorage = MemoryStorage()

ymj_base_url = 'https://elk.yimeijian.cn/v1/'

# 发起小程序授权回调
ymj_start_auth_callback = ymj_base_url + 'ab/proxy_wxapp/auth_callback/'
# 授权结束后回调页面
ymj_end_auth_callback = '.yimeijian.cn/#/setting/small_program_auth'

#  微信授权URL
wx_auth_url = 'https://mp.weixin.qq.com/cgi-bin/componentloginpage?component_appid='
# 体验二维码
wx_qrcode_url = 'https://api.weixin.qq.com/wxa/get_qrcode?access_token='


def wxapp_auth_view(request, merchant_id):
    """
    发起小程序授权 mb-request-wxapp-auth
    :param request:
    :return:
    """
    callback_url = ymj_start_auth_callback + str(merchant_id) + '/'
    token = component.access_token
    logger.debug("wechat access_token: " + str(token))
    pre_code_dct = component.create_preauthcode()
    logger.debug("wechat pre_code: " + str(pre_code_dct))
    pre_code = pre_code_dct['pre_auth_code']
    url = wx_auth_url + WE_CHAT_APP['APP_ID'] + '&pre_auth_code=' + pre_code + '&redirect_uri=' + callback_url
    return render(request, 'wxapps/auth.html', {'auth_url': url})


class AuthCallback(views.APIView):
    """
    小程序扫描二维码授权回调 ab-proxy-wxapp-auth-callback
    :return:
    """
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(
                name='merchant_id',
                schema=coreschema.String,
                location='form',
                required=True,
                description='merchant_id',
            )
        ]
    )

    def get(self, request, merchant_id):
        logger.debug("wechat auth_callback merchant_id : " + str(merchant_id))
        auth_code = request.GET.get('auth_code', '')
        merchant = Merchant.objects.get(id=merchant_id)
        if merchant:
            result = component.query_auth(auth_code)
            authorizer_appid = result['authorization_info']['authorizer_appid']
            logger.debug("wechat 小程序扫描二维码授权回调 authorizer_appid :" + str(authorizer_appid))
            auth_info = memorystorage.get(key=authorizer_appid)
            if auth_info:
                logger.debug("wechat auth_info: " + str(auth_info))
                memorystorage.delete(authorizer_appid)
                app_id = auth_info['authorizer_appid']
                access_token = auth_info['authorizer_access_token']
                refresh_token = auth_info['authorizer_refresh_token']
                wx_mch_user = wx_mch_user_create_or_update(app_id=app_id, access_token=access_token,
                                                           refresh_token=refresh_token)
                update_merchant_config(merchant, wx_mch_user)

                # 设置域名
                logger.debug("wechat modify_domain start =============")
                result = wechat_api.modify_domain(access_token, 'set', WE_CHAT_APP['REQUEST_DOMAIN'],
                                                  WE_CHAT_APP['WSREQUEST_DOMAIN'], WE_CHAT_APP['UPLOAD_DOMAIN'],
                                                  WE_CHAT_APP['DOWNLOAD_DOMAIN'])
                if result[0]:
                    logger.debug('wechat modify_domain is ok')
                logger.debug("wechat modify_domain end =============")

                # 小程序提交模板代码
                result, template_list = wechat_api.template_list(str(component.access_token))
                logger.debug('wechat template_list: ' + str(template_list))
                if len(template_list):
                    logger.debug("wechat template_list size: " + str(len(template_list)))
                    template = template_list[len(template_list) - 1]
                    f = open('b2c/wxapp/config/app.json', 'r')
                    ext_str = f.read()
                    ext_json = json.loads(ext_str)
                    logger.debug('wechat name_code: ' + str(merchant.name_code))
                    ext_json['ext']['name_code'] = merchant.name_code
                    ext_json['ext']['title'] = merchant.name
                    code_commit = wechat_api.commit_code(access_token, template['template_id'],
                                                         json.dumps(ext_json), template['user_version'],
                                                         template['user_desc'])
                    logger.debug("wechat commit finish--------------------" + str(code_commit))
                    # 小程序提交审核
                    category_tp = wechat_api.app_category_list(access_token)
                    logger.debug("wechat detail category_tp: " + str(category_tp))
                    wechat_api.undocodeaudit(access_token)
                    status_code, result = wechat_api.submit_audit(access_token=access_token, category_list=None)
                    if status_code:
                        wx_mch_user_create_or_update(app_id=app_id,
                                                     app_review_status=WXAppReviewStateType.PROCESSING.value,
                                                     app_version=template['user_version'],
                                                     app_submitted_at=datetime.now())
                        logger.debug('wechat submit success: result -> ' + str(result))
        redirect_url = 'https://' + merchant.name_code + ymj_end_auth_callback
        return HttpResponseRedirect(redirect_url)


class WeChatAuthCallbackView(views.APIView):
    """
    代小程序授权回调接口（微信10分钟回调一次）ab-proxy-wxapp-auth
    """

    def post(self, request):
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        msg_signature = request.GET.get('msg_signature', '')
        logger.debug("wechat callback start 66666")
        msg = component.parse_message(request.body, msg_signature, timestamp, nonce)
        if msg.type in ('authorized', 'updateauthorized'):
            logger.debug('wechat authorized or updateauthorized msg: ' + str(msg))
            auth_result = msg.query_auth_result
            auth_info = auth_result['authorization_info']
            authorizer_access_token = auth_info['authorizer_access_token']
            authorizer_refresh_token = auth_info['authorizer_refresh_token']
            authorizer_appid = auth_info['authorizer_appid']
            memorystorage.set(key=authorizer_appid, value=auth_info)
            logger.debug("wechat authorizer_access_token: " + str(authorizer_access_token))
            logger.debug("wechat authorizer_refresh_token: " + str(authorizer_refresh_token))
            logger.debug('wechat authorizer_appid:' + authorizer_appid)
        elif msg.type == 'unauthorized':
            logger.debug('wechat unauthorized msg: ' + str(msg))
            logger.debug('wechat unauthorized msg AppId:' + str(msg.authorizer_appid))
            if msg.authorizer_appid:
                cancel_authorize(msg.authorizer_appid)
        else:
            component.access_token
            logger.debug("wechat callback component.access_token : " + str(component.access_token))
            wechat_api.template_list(str(component.access_token))
            logger.debug("wechat ticket : " + msg.verify_ticket)
        return Response('success')


class WeChatCurrentDetail(SimpleCodenamePermissionMixin):
    """
    获取授权小程序的详细信息 mb-wxapp-detail
    """
    permission_codenames = ['users.mb_binding_wx_applet']

    def post(self, request):
        merchant = get_merchant_from_merchant_user(request)
        if merchant.config:
            wx_mch_user = merchant.config.wx_mch_user
            if wx_mch_user:
                access_token = get_access_token(wx_mch_user.id)
                dct = dict()
                auth_info = component.get_authorizer_info(wx_mch_user.app_id)
                logger.debug("wechat detail info: " + str(auth_info))
                if auth_info:
                    base_auth_info = dict()
                    base_auth_info['principal_name'] = auth_info['authorizer_info']['principal_name']
                    base_auth_info['head_img'] = auth_info['authorizer_info']['head_img']
                    base_auth_info['signature'] = auth_info['authorizer_info']['signature']
                    dct['base_info'] = base_auth_info
                    logger.debug('wechat detail: ' + str(dct))
                category_tp = wechat_api.app_category_list(str(access_token))
                if category_tp[0]:
                    dct['category_list'] = category_tp[1]['category_list']
                return Response(dct, status=status.HTTP_200_OK)
        return Response("未授权", status=status.HTTP_400_BAD_REQUEST)


class WeChatQrCode(views.APIView):
    """
    获取小程序体验二维码
    指定体验版二维码跳转到某个具体页面（如果不需要的话，则不需要填path参数，可在路径后以“?参数”方式传入参数）
    具体的路径加参数需要urlencode，比如page/index?action=1编码后得到page%2Findex%3Faction%3D1
    code mb-wxapp-wxa-code
    """
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(
                name='path',
                schema=coreschema.String,
                location='form',
                required=True,
                description='指定体验版二维码跳转到某个具体页面',
            )
        ]
    )

    permission_classes = (IsMerchantUserPermission,)

    def get(self, request):
        path = request.data.get('path', None)
        merchant_id = request.merchant_id
        wx_mch_user = MerchantConfig.objects.get(merchant_id=merchant_id).wx_mch_user
        if wx_mch_user:
            if not path:
                path = 'pages/index/index'
            from b2c.wxapp.services import get_wxa_code
            image_content, is_image = get_wxa_code(mch_user_id=wx_mch_user.id, wxa_path=path)
            if not is_image:
                access_token = get_access_token(wx_mch_user.id)
                url = wx_qrcode_url + str(access_token) + ('&path=' + path if path else '')
                rep = requests.get(url)
                if 'image' not in rep.headers['Content-Type']:
                    return None
                else:
                    return HttpResponse(rep.content, content_type='image/png')
            else:
                return HttpResponse(image_content, content_type='image/png')
        else:
            return Response("未授权", status=status.HTTP_400_BAD_REQUEST)


class WXAppShareCode(views.APIView):
    """
    获取小程序分享二维码 mb-wxapp-detail
    """

    def get(self, request):
        merchant_id = request.merchant_id
        wx_mch_user_id = MerchantConfig.objects.get(merchant_id=merchant_id).wx_mch_user.id
        wxa_path = request.query_params['wxa_path']
        wxa_scene = request.query_params['wxa_scene']
        from b2c.wxapp.services import get_wxa_code
        image_content, _ = get_wxa_code(mch_user_id=wx_mch_user_id, wxa_path=wxa_path, scene=wxa_scene)
        return HttpResponse(image_content, content_type='image/png')


class AuditAllMerchant(views.APIView):
    """
    用最新模版提交商户小程序
    """

    def post(self, request):
        submit_audit_all_merchant()
        return Response('ok', status=status.HTTP_200_OK)


class AuditeCallback(views.APIView):
    """
    微信消息&事件回调接口（代小程序） ab-proxy-wxapp-events
    """

    def post(self, request, app_id):
        logger.debug("wechat audite callback appId : " + app_id)
        logger.debug("wechat audite callback msg : " + str(request.body))
        return HttpResponse('success')
