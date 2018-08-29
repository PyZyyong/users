from datetime import datetime

from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status, mixins
from rest_framework_jwt.views import JSONWebTokenAPIView, jwt_response_payload_handler

from b2c.general.mixins import SimpleCodenamePermissionMixin
from b2c.users.models import User, MerchantUser
from b2c.users.permissions import IsMerchantUserPermission
from b2c.users.serializers import user_serializer
from config.settings.base import JWT_AUTH


class LoginView(JSONWebTokenAPIView):
    """
    JWT login
    """
    serializer_class = user_serializer.UserLoginSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        """
        用户登录，返回JWT Token
        fe-user-login
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = user_serializer.UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if JWT_AUTH['JWT_AUTH_COOKIE']:
                expiration = (datetime.utcnow() +
                              JWT_AUTH['JWT_EXPIRATION_DELTA'])
                response.set_cookie(JWT_AUTH['JWT_AUTH_COOKIE'],
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin,
                  SimpleCodenamePermissionMixin):
    """
    list: 商户用户列表	  mb-users
    create: 商户用户创建	mb-create-user
    retrieve: 商户用户详情	  mb-user-detail
    """
    filter_class = []
    permission_codenames = ['users.mb_merchant_user_manage']
    permission_classes = (IsMerchantUserPermission,)
    escape_actions = ['current']

    def get_queryset(self):
        if self.action == 'list':
            merchant_id = self.request.merchant_id
            queryset = MerchantUser.objects.filter(merchant_id=merchant_id).order_by('-date_joined')
            return queryset

        queryset = MerchantUser.objects.all().order_by('-date_joined')
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return user_serializer.MerchantUserRetrieveSerializer
        if self.action == 'enable':
            return user_serializer.MerchantEnableSerializer
        if self.action == 'disable':
            return user_serializer.MerchantDisableSerializer
        if self.action == 'current':
            return user_serializer.CurrentUserSerializer
        if self.action == 'list':
            return user_serializer.MerchantUserListSerializer
        if self.action == 'create':
            return user_serializer.MerchantUserCreateSerializer
        return user_serializer.MerchantUserSerializer

    @action(methods=['get'], detail=False)
    def current(self, request):
        """
        获取当前登录用户信息 mb-current-user
        :param request:
        :return:
        """
        user = request.user
        serializer = self.get_serializer(instance=user)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        商户用户修改 mb-update-user
        :param request:
        :param pk:
        :return:
        """
        user = MerchantUser.objects.get(id=pk)
        serializer = self.get_serializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def disable(self, request, pk=None):
        """
        商户用户 禁用 mb-disable-user
        :param request:
        :param pk:
        :return:
        """
        user = User.objects.get(id=pk)
        serializer = self.get_serializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": 'success'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def enable(self, request, pk=None):
        """
        商户用户 启用 mb-enable-user
        :param request:
        :param pk:
        :return:
        """
        user = User.objects.get(id=pk)
        serializer = self.get_serializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": 'success'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckPhoneView(GenericViewSet, SimpleCodenamePermissionMixin):

    permission_codenames = ['users.mb_merchant_user_manage']
    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        return queryset

    def get_serializer_class(self):
        return user_serializer.MerchantUserSerializer

    @action(methods=['get'], detail=False)
    def phone(self, request):
        """
        商户用户检查手机 mb-check-user-phone
        :param request:
        :return:
        """
        number = request.query_params.get('phone', '')
        if number:
            users = User.objects.filter(mobile_number=number)
            serializer = user_serializer.MerchantUserSerializer(users, many=True)
            code = users.exists()
            resp = {
                'code': code,
                'data': serializer.data
            }
            return Response(resp, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)
