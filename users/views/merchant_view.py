import coreapi
import coreschema
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework import views
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.settings import api_settings

from b2c.general.exceptions import ServiceValidationError
from b2c.general.helpers import get_merchant_from_merchant_user
from b2c.general.mixins import SimpleCodenamePermissionMixin
from b2c.misc.serializers.media_upload_serializer import MediaUploadSerializer
from b2c.users.decorators.decorator import merchant_user_required
from b2c.users.models import Merchant, MerchantCard, MerchantUser
from b2c.users.permissions import IsMerchantUserPermission
from b2c.users.serializers import merchant_serializer
from b2c.users.services import obtain_merchant_user_login_sms_code, verify_merchant_user_login_sms_code
from b2c.wxapp.services import update_mch_user_cert

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class MerchantSMSCodeVerifyView(views.APIView):
    """
    验证登录验证码（并返回jwt token） mb-verify-login-sms-code
    """
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(
                name='code',
                schema=coreschema.String,
                location='form',
                required=True,
                description='验证码',
            ),
            coreapi.Field(
                name='mobile_number',
                schema=coreschema.String,
                location='form',
                required=True,
                description='手机号',
            )
        ],
    )

    def post(self, request):
        code = request.data.get('code', None)
        if code is None:
            raise ValidationError('请填写验证码')
        mobile_number = request.data.get('mobile_number', None)
        if not mobile_number:
            raise ValidationError('请输入手机号')

        user = get_object_or_404(MerchantUser,
                                 merchant_id=request.merchant_id,
                                 mobile_number=mobile_number)
        if not verify_merchant_user_login_sms_code(user_id=user.id,
                                                   code=str(code)):
            raise ValidationError('验证码不匹配')
        # 返回jwt token
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return Response({'token': token}, status=status.HTTP_200_OK)


class MerchantSMSCodeObtainView(views.APIView):
    """
    获取登录验证码 mb-obtain-login-sms-code
    """
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(
                name='mobile_number',
                schema=coreschema.String,
                location='form',
                required=True,
                description='手机号',
            )
        ]
    )

    def post(self, request):
        mobile_number = request.data.get('mobile_number', None)
        if not mobile_number:
            raise ValidationError('请输入手机号')

        user = get_object_or_404(MerchantUser,
                                 merchant_id=request.merchant_id,
                                 mobile_number=mobile_number)
        obtain_merchant_user_login_sms_code(user_id=user.id)
        return Response(status=status.HTTP_200_OK)


class MerchantViewSet(GenericViewSet, SimpleCodenamePermissionMixin):
    permission_codenames = ['users.mb_wx_pay_auth']
    permission_classes = (IsMerchantUserPermission,)
    escape_actions = ['my']

    def get_queryset(self):
        return Merchant.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.action == 'my':
            return merchant_serializer.MerchantSerializer
        elif self.action == 'merchant_wxapp':
            return merchant_serializer.MerchantWXAppSerializer

    @action(methods=['get'], detail=False)
    def my(self, request):
        """
        当前商户信息 mb-my-merchant-info
        :param request:
        :return:
        """
        user = request.user
        merchant = user.merchantuser.merchant
        serializer = self.get_serializer(instance=merchant)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get', 'put'], detail=False)
    def merchant_wxapp(self, request, *args, **kwargs):
        """
        商户微信支付设置 mb-get-mechant-wxapp mb-update-mechant-wxapp
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user = request.user
        merchant = user.merchantuser.merchant
        if request.method.lower() == 'put':
            wx_mch_user_id = merchant.config.wx_mch_user.id
            mch_id = request.data['mch_id']
            sign_key = request.data['sign_key']
            cert_pem = request.data['cert_pem']
            key_pem = request.data['key_pem']
            update_mch_user_cert(
                wx_mch_user_id=wx_mch_user_id,
                mch_id=mch_id,
                sign_key=sign_key,
                cert_pem_uuid=cert_pem,
                key_pem_uuid=key_pem
            )
            return Response(status=status.HTTP_201_CREATED)
        else:
            serializer = self.get_serializer(instance=merchant)
            return Response(serializer.data, status=status.HTTP_200_OK)


class MerchantAuthView(SimpleCodenamePermissionMixin, GenericViewSet):
    permission_codenames = ["users.mb_merchant_auth"]

    def get_serializer_class(self):
        if self.action == 'auth1':
            return merchant_serializer.MerchantAuth1Serializer
        if self.action == 'auth2':
            return merchant_serializer.MerchantAuth2Serializer

    @method_decorator(merchant_user_required())
    @action(methods=['patch'], detail=False)
    def auth1(self, request):
        """
        商户认证1	mb-auth-merchant-1
        :param request:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(merchant_user_required())
    @action(methods=['patch'], detail=False)
    def auth2(self, request):
        """
        商户认证2	mb-auth-merchant-2
        :param request:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(merchant_user_required())
    @action(methods=['get'], detail=False)
    def auth_state(self, request):
        """
        商户认证状态查询 mb-auth-merchant-state
        :param request:
        :return:
        """
        merchant = get_merchant_from_merchant_user(request)
        state = merchant.authenticated_state
        return Response(state, status=status.HTTP_200_OK)


class MerchantCardView(SimpleCodenamePermissionMixin):

    permission_codenames = ['users.mb_merchant_card']

    def get(self, request):
        """
        我的商户卡 mb-my-merchant-card
        :param request:
        :return:
        """
        merchant_id = self.request.merchant_id
        merchant_card = MerchantCard.objects.filter(merchant_id=merchant_id).first()
        if not merchant_card:
            raise ServiceValidationError('该商户还未创建商户卡，请先创建！')
        images = merchant_card.images.all()
        media_serializer = MediaUploadSerializer(
            images,
            context={'request': request},
            many=True
        )
        serializer = merchant_serializer.MerchantCardSerializer(
            instance=merchant_card
        )
        data = serializer.data
        data['images'] = media_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        修改我的商户卡 mb-update-my-merchant-card
        :param request:
        :return:
        """
        merchant_id = request.merchant_id
        merchant = Merchant.objects.get(id=merchant_id)
        serializer = merchant_serializer.MerchantCardUpdateSerializer(
            instance=merchant,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'success'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
