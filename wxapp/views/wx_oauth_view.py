from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from b2c.wxapp.models.wx_mch_cert_type import WXMchCertType
from b2c.wxapp.models.wx_mch_user import WXMchUser
from b2c.wxapp.serializers.wx_oauth_serializer import WXOAuthSerializer
from b2c.wxapp.services import wx_user_login, wx_mch_user_create, wx_user_phone_decrypt, get_wxa_code, \
    update_mch_user_cert_by_type


class WXOAuthViewSet(viewsets.ModelViewSet):
    """
    微信用户授权验证
    """
    queryset = WXMchUser.objects.all()
    serializer_class = WXOAuthSerializer

    @action(methods=['get'], detail=False)
    def user_login(self, request):
        user_code = request.query_params.get('code')
        mch_user_id = request.query_params.get('mch_user_id')
        result = wx_user_login(mch_user_id, user_code)
        if result:
            rep = {'msg': 'success', 'code': 200, 'data': result.token}
        else:
            rep = {'msg': 'error', 'code': 400, 'data': result}
        return Response(rep)

    @action(methods=['get'], detail=False)
    def user_phone(self, request):
        token = request.query_params.get('token')
        mch_user_id = request.query_params.get('mch_user_id')
        encrypted_data = request.query_params.get('encrypted_data')
        iv = request.query_params.get('iv')
        app_user = wx_user_phone_decrypt(
            token=token, mch_user_id=mch_user_id, encrypted_data=encrypted_data, iv=iv)
        rep = {'msg': 'success', 'code': 200, 'data': app_user.phone_number}
        return Response(rep)

    @action(methods=['get'], detail=False)
    def add_mch_for_test(self, request):
        # TODO del
        app_id = 'wx1e4291c8ceef9d49'
        secret = '9d7eee69ceed92db3762544153486f39'
        mch_id = '1508858091'
        mch_user = wx_mch_user_create(app_id=app_id, mch_id=mch_id, refresh_token='', )
        rep = {'msg': 'success', 'code': 200, 'data': mch_user.id}
        return Response(rep)

    @action(methods=['get'], detail=False)
    def qr_code_for_test(self, request):
        mch_user_id = request.query_params['mch_user_id']
        wxa_path = request.query_params['wxa_path']
        image_content, _ = get_wxa_code(mch_user_id=mch_user_id, wxa_path=wxa_path)
        return HttpResponse(image_content, content_type='image/png')

    @action(methods=['post'], detail=False)
    def update_mch_cert_for_test(self, request):
        cert_type = request.data['cert_type']
        uuid = request.data['uuid']
        mch_user_id = request.data['mch_user_id']
        mch_user = update_mch_user_cert_by_type(wx_mch_user_id=mch_user_id, cert_type=WXMchCertType(cert_type),
                                                uuid=uuid)
        rep = {'msg': 'success', 'code': 200, 'data': mch_user.id}
        return Response(rep)
