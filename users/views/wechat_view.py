# import logging
# import os
# import pickle
# import json
#
# import coreapi
# import coreschema
# import requests
# from django.http import HttpResponseRedirect, HttpResponse
# from django.shortcuts import render
# from rest_framework import status
# from rest_framework import views
# from rest_framework.response import Response
# from rest_framework.schemas import AutoSchema
# from wechatpy import WeChatComponent
# from wechatpy.session import SessionStorage
# from wechatpy.session.memorystorage import MemoryStorage
#
# from b2c.general.helpers import get_merchant_from_merchant_user
# from b2c.users import wechat_api
# from b2c.users.models import MerchantConfig
# from b2c.users.models.merchant import Merchant
# from b2c.wxapp.services import wx_mch_user_create_or_update, get_access_token
# from b2c.users.services import update_merchant_config, get_merchant_name_code
# from config.settings.base import WE_CHAT_APP
#
#
# class FileSessionStorage(SessionStorage):
#     def __init__(self):
#         self._data = {}
#
#     def _save(self):
#         pickle.dump(self._data, open('/data/b2c_runtime/wx_session.p', 'wb'))
#
#     def _load(self):
#         if os.path.getsize('/data/b2c_runtime/wx_session.p') > 0:
#             self._data = pickle.load(open('/data/b2c_runtime/wx_session.p', 'rb'))
#
#     def get(self, key, default=None):
#         self._load()
#         return self._data.get(key, default)
#
#     def set(self, key, value, ttl=None):
#         if value is None:
#             return
#         self._data[key] = value
#         self._save()
#
#     def delete(self, key):
#         self._data.pop(key, None)
#         self._save()
#
#
# logger = logging.getLogger('django')
# component = WeChatComponent(WE_CHAT_APP.get('APP_ID'), WE_CHAT_APP.get('APP_SECRET'),
#                             WE_CHAT_APP.get('TOKEN'), WE_CHAT_APP.get('ENCODING_KEY'),
#                             session=FileSessionStorage())
# memorystorage = MemoryStorage()
#
#
# def wxapp_auth_view(request, merchant_id):
#     """
#     发起小程序授权 mb-request-wxapp-auth
#     :param request:
#     :return:
#     """
#     callback_url = 'https://elk.yimeijian.cn/v1/ab/proxy_wxapp/auth_callback/' + str(merchant_id) + '/'
#     logger.debug("wechat callback_url: " + callback_url)
#     token = component.access_token
#     logger.debug("wechat access_token: " + str(token))
#     pre_code_dct = component.create_preauthcode()
#     logger.debug("wechat pre_code: " + str(pre_code_dct))
#     pre_code = pre_code_dct['pre_auth_code']
#     url = 'https://mp.weixin.qq.com/cgi-bin/componentloginpage?component_appid=' + WE_CHAT_APP.get('APP_ID') + \
#           '&pre_auth_code=' + pre_code + '&redirect_uri=' + callback_url + '&auth_type=3'
#     return render(request, 'wxapps/auth.html', {'auth_url': url})
#
#
# class AuthCallback(views.APIView):
#     """
#     小程序扫描二维码授权回调 ab-proxy-wxapp-auth-callback
#     :return:
#     """
#     schema = AutoSchema(
#         manual_fields=[
#             coreapi.Field(
#                 name='merchant_id',
#                 schema=coreschema.String,
#                 location='form',
#                 required=True,
#                 description='merchant_id',
#             )
#         ]
#     )
#
#     def get(self, request, merchant_id):
#         logger.debug("wechat auth_callback merchant_id : " + str(merchant_id))
#         auth_code = request.GET.get('auth_code', '')
#         merchant = Merchant.objects.get(id=merchant_id)
#         if merchant:
#             result = component.query_auth(auth_code)
#             authorizer_appid = result['authorization_info']['authorizer_appid']
#             logger.debug("wechat 小程序扫描二维码授权回调 authorizer_appid :" + str(authorizer_appid))
#             auth_info = memorystorage.get(key=authorizer_appid)
#             if auth_info:
#                 logger.debug("wechat auth_info: " + str(auth_info))
#                 memorystorage.delete(authorizer_appid)
#                 auth_info = json.loads(auth_info)
#                 wx_mch_user = wx_mch_user_create_or_update(appid_id=auth_info['authorizer_appid'],
#                                                            access_token=auth_info['authorizer_access_token'],
#                                                            refresh_token=auth_info[
#                                                                'authorizer_refresh_token'])
#                 config = merchant.config
#                 if config:
#                     logger.debug("wechat auth_callback merchant_id config exist")
#                     update_merchant_config(merchant, wx_mch_user)
#         redirect_url = 'http://demo1.yimeijian.cn/#/setting/small_program_auth'
#         return HttpResponseRedirect(redirect_url)
#
#
# class WeChatAuthCallbackView(views.APIView):
#     """
#     代小程序授权回调接口（微信10分钟回调一次）ab-proxy-wxapp-auth
#     """
#
#     def post(self, request):
#         timestamp = request.GET.get('timestamp', '')
#         nonce = request.GET.get('nonce', '')
#         msg_signature = request.GET.get('msg_signature', '')
#         logger.debug("wechat callback start 66666")
#         msg = component.parse_message(request.body, msg_signature, timestamp, nonce)
#         if msg.type in ('authorized', 'updateauthorized'):
#             logger.debug('wechat authorized or updateauthorized msg: ' + str(msg))
#             """
#             {
#                 "authorization_info": {
#                     "authorizer_appid": "wxf8b4f85f3a794e77",
#                     "authorizer_access_token": "QXjUqNqfYVH0yBE1iI_7vuN_9gQbpjfK7hYwJ3P7xOa88a89",
#                     "expires_in": 7200,
#                     "authorizer_refresh_token": "dTo-YCXPL4llX-u1W1pPpnp8Hgm4wpJtlR6iV0doKdY",
#                 }
#             }
#             """
#             auth_result = msg.query_auth_result
#             auth_info = auth_result['authorization_info']
#             logger.debug("wechat auth_info: " + str(auth_info))
#             authorizer_access_token = auth_info['authorizer_access_token']
#             authorizer_refresh_token = auth_info['authorizer_refresh_token']
#             authorizer_appid = auth_info['authorizer_appid']
#             memorystorage.set(key=authorizer_appid, value=str(auth_info))
#             logger.debug("wechat authorizer_access_token: " + str(authorizer_access_token))
#             logger.debug("wechat authorizer_refresh_token: " + str(authorizer_refresh_token))
#             logger.debug('wechat authorizer_appid:' + authorizer_appid)
#
#             client = component.get_client_by_appid(authorizer_appid)
#             logger.debug("wechat access_token: " + str(client.access_token))
#
#             # 设置域名
#             logger.debug("wechat modify_domain start =============")
#             result = wechat_api.modify_domain(str(client.access_token), 'add', ['https://elk.yimeijian.cn'],
#                                               ['wss://elk.yimeijian.cn'], ['https://elk.yimeijian.cn'],
#                                               ['https://elk.yimeijian.cn'])
#             if result[0]:
#                 logger.debug('wechat modify_domain is ok')
#             logger.debug("wechat modify_domain end =============")
#
#             # 小程序提交模板代码
#             logger.debug("wechat component.access_token : " + str(component.access_token))
#             result, template_list = wechat_api.template_list(str(component.access_token))
#             logger.debug('wechat template_list: ' + str(template_list))
#             if len(template_list):
#                 logger.debug("wechat template_list size: " + str(len(template_list)))
#                 template = template_list[0]
#                 f = open('b2c/wxapp/config/app.json', 'r')
#                 ext_str = f.read()
#                 ext_json = json.loads(ext_str)
#                 name_code = get_merchant_name_code(authorizer_appid)
#                 logger.debug('wechat name_code: ' + str(name_code))
#                 ext_json['ext']['name_code'] = name_code
#                 code_commit = wechat_api.commit_code(str(client.access_token), template['template_id'],
#                                                      json.dumps(ext_json), template['user_version'],
#                                                      template['user_desc'])
#                 logger.debug("wechat commit finish--------------------" + str(code_commit))
#
#                 # 小程序基本信息
#                 # dct = dict()
#                 # auth_info = component.get_authorizer_info(authorizer_appid)
#                 # logger.debug("wechat detail info: " + str(auth_info))
#                 # if auth_info:
#                 #     base_auth_info = dict()
#                 #     base_auth_info['principal_name'] = auth_info['authorizer_info']['principal_name']
#                 #     base_auth_info['head_img'] = auth_info['authorizer_info']['head_img']
#                 #     base_auth_info['signature'] = auth_info['authorizer_info']['signature']
#                 #     logger.debug('wechat detail: ' + str(base_auth_info))
#
#                 # 小程序提交审核
#                 # category_tp = wechat_api.app_category_list(str(client.access_token))
#                 # logger.debug("wechat detail category_tp: " + str(category_tp))
#                 # status_code, result = wechat_api.submit_audit(access_token=str(client.access_token), category_list=None)
#                 # if status_code:
#                 #     logger.debug('wechat submit success: result -> ' + str(result))
#
#         elif msg.type == 'unauthorized':
#             logger.debug('wechat unauthorized msg: ' + str(msg))
#             """
#             OrderedDict([('AppId', 'wx3fd3c977e8d26657'), ('CreateTime', '1532696164'), ('InfoType', 'unauthorized'),
#              ('AuthorizerAppid', 'wx13edb53d3d7988ba')])
#             """
#             # authorizer_appid = msg.authorizer_appid
#             # app_id = msg.appid
#         else:
#             component.access_token
#             logger.debug("wechat component.access_token : " + str(component.access_token))
#             wechat_api.template_list(str(component.access_token))
#             logger.debug("wechat ticket : " + msg.verify_ticket)
#         return Response('success')
#
#
# class WeChatCurrentDetail(views.APIView):
#     """
#     获取授权小程序的详细信息 mb-wxapp-detail
#     """
#
#     def post(self, request):
#         merchant = get_merchant_from_merchant_user(request)
#         wx_mch_user = merchant.config.wx_mch_user
#         if wx_mch_user:
#             access_token = get_access_token(wx_mch_user.id)
#             logger.debug("wechat access_token: " + access_token)
#             dct = dict()
#             # auth_info = component.get_authorizer_info(authorizer_appid)
#             # logger.debug("wechat detail info: " + str(auth_info))
#             # if auth_info:
#             #     base_auth_info = dict()
#             #     base_auth_info['principal_name'] = auth_info['authorizer_info']['principal_name']
#             #     base_auth_info['head_img'] = auth_info['authorizer_info']['head_img']
#             #     base_auth_info['signature'] = auth_info['authorizer_info']['signature']
#             #     dct['base_info'] = base_auth_info
#             #     logger.debug('wechat detail: ' + str(dct))
#             category_tp = wechat_api.app_category_list(str(access_token))
#             if category_tp[0]:
#                 dct['category_list'] = category_tp[1]
#             return Response(dct, status=status.HTTP_200_OK)
#         else:
#             return Response("未授权", status=status.HTTP_400_BAD_REQUEST)
#
#
# class WeChatQrCode(views.APIView):
#     """
#     获取小程序体验二维码
#     指定体验版二维码跳转到某个具体页面（如果不需要的话，则不需要填path参数，可在路径后以“?参数”方式传入参数）
#     具体的路径加参数需要urlencode，比如page/index?action=1编码后得到page%2Findex%3Faction%3D1
#     code mb-wxapp-wxa-code
#     """
#     schema = AutoSchema(
#         manual_fields=[
#             coreapi.Field(
#                 name='path',
#                 schema=coreschema.String,
#                 location='form',
#                 required=True,
#                 description='指定体验版二维码跳转到某个具体页面',
#             )
#         ]
#     )
#
#     def get(self, request):
#         path = request.data.get('path', None)
#         merchant = get_merchant_from_merchant_user(request)
#         wx_mch_user = merchant.config.wx_mch_user
#         if wx_mch_user:
#             access_token = get_access_token(wx_mch_user.id)
#             if path:
#                 url = 'https://api.weixin.qq.com/wxa/get_qrcode?access_token=' + str(access_token) + '&path=' + path
#             else:
#                 url = 'https://api.weixin.qq.com/wxa/get_qrcode?access_token=' + str(access_token)
#             return requests.get(url)
#         else:
#             return Response("未授权", status=status.HTTP_400_BAD_REQUEST)
#
#
# class WXAppShareCode(views.APIView):
#     """
#     获取小程序分享二维码 mb-wxapp-detai
#     """
#
#     def get(self, request):
#         merchant_id = request.merchant_id
#         wx_mch_user_id = MerchantConfig.objects.get(merchant_id=merchant_id).wx_mch_user.id
#         wxa_path = request.query_params['wxa_path']
#         wxa_scene = request.query_params['wxa_scene']
#         from b2c.wxapp.services import get_wxa_code
#         image_content = get_wxa_code(mch_user_id=wx_mch_user_id, wxa_path=wxa_path, scene=wxa_scene)
#         return HttpResponse(image_content, content_type='image/png')
