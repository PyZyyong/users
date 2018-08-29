import logging
from datetime import datetime

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from rest_framework import status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from b2c.coupons.services import get_front_user_count
from b2c.misc.models import Media
from b2c.misc.serializers import MediaRefSerializer
from b2c.orders.services import get_front_user_status_statistics
from b2c.users.decorators.decorator import frontend_user_required
from b2c.users.models import FrontendUser, MerchantConfig
from b2c.users.permissions import IsFrontendUserPermission
from b2c.users.serializers_fe import frontend_user_serializer
from b2c.users.services import frontend_user_phone_decrypt, update_frontend_user, update_avatar_from_wx, \
    get_user_joined_days, get_login_ip, fe_wx_user_login_old, fe_wx_user_login
from b2c.wxapp.services import get_wxa_code, wx_app_user_update


class FrontendUserView(GenericViewSet):
    """
    frontend user view 微信用户授权验证
    """
    # permission_classes = (IsFrontendUserPermission, )
    queryset = FrontendUser.objects.all()
    serializer_class = frontend_user_serializer.FrontendCurrentSerializer

    @method_decorator(frontend_user_required())
    @action(methods=['get'], detail=False)
    def current(self, request):
        """
        当前用户 fe-current-user
        :param request:
        :return:
        """
        user = request.user.frontenduser
        serializer = frontend_user_serializer.FrontendCurrentSerializer(instance=user)
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def login_old(self, request):
        """
        用户登录 fe-user-login
        :param request:
        :return:
        """
        merchant_id = self.request.merchant_id
        user_code = request.data.get('code')
        result = fe_wx_user_login_old(merchant_id, user_code)
        if result:
            get_login_ip(request, user_id=result.id)
            return Response({'msg': 'success', 'data': result.frontenduser.wx_user.token}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'error', }, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)
    def login(self, request):
        """
        用户登录 fe-user-login
        :param request:
        :return:
        """
        merchant_id = self.request.merchant_id
        user_code = request.data.get('code')
        result = fe_wx_user_login(merchant_id, user_code)
        if result:
            get_login_ip(request, user_id=result.id)
            return Response({'msg': 'success', 'data': result.frontenduser.wx_user.token}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'error', }, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(frontend_user_required())
    @action(methods=['post'], detail=False)
    def decrypt_mobile_phone(self, request):
        """
        解密数据（手机）fe-user-decrypt-mobile-number
        :param request:
        :return:
        """
        mch_id = request.merchant_id
        front_user = request.user
        encrypted_data = request.data.get('encrypted_data')
        iv = request.data.get('iv')
        frontend_user = frontend_user_phone_decrypt(
            token=front_user.wx_user.token, mch_id=mch_id, encrypted_data=encrypted_data, iv=iv)
        if frontend_user:
            rep = {'msg': 'success', 'data': frontend_user.mobile_number}
            return Response(rep)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # @action(methods=['post'], detail=False)
    # def decrypt_profile(self, request):
    #     """
    #     解密数据（用户信息）
    #     (fe-user-decrypt-profile)
    #     :param request:
    #     :return:
    #     """
    #     mch_id = request.merchant_id
    #     front_user = request.user
    #     encrypted_data = request.data.get('encrypted_data')
    #     iv = request.data.get('iv')
    #     frontend_user = frontend_user_info_decrypt(
    #         token=front_user.wx_user.token, mch_id=mch_id, encrypted_data=encrypted_data, iv=iv)
    #     if frontend_user:
    #         return Response(status=status.HTTP_200_OK)
    #     else:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(frontend_user_required())
    @action(methods=['post'], detail=False)
    def decrypt_profile(self, request):
        """
        解密数据（用户信息）fe-user-decrypt-profile
        :param request:
        :return:
        """
        frontend_user = request.user.frontenduser
        wx_user = frontend_user.wx_user
        mch_user = wx_user.mch_user
        data = request.data
        logging.getLogger('django.server').debug(f'from wx user data:{data}')
        # 同步微信用户信息
        wx_app_user_update(
            app_user_id=wx_user.id,
            mch_user_id=mch_user.id,
            nick_name=data.get('nickName'),
            avatar_url=data.get('avatarUrl'),
            gender=data.get('gender', 2),
            language=data.get('language', None),
            phone_number=data.get('mobile_number', None),
        )
        # 判断是否需要更新
        if not frontend_user.is_synced_from_wx or \
                not all([frontend_user.avatar, frontend_user.display_name]):
            logging.getLogger('django.server').debug('update frontend user from wx')
            user = update_frontend_user(
                frontend_user_id=frontend_user.id,
                is_merchant_user=False,
                is_admin_user=False,
                is_frontend_user=True,
                display_name=data.get('nickName') if not frontend_user.display_name else frontend_user.display_name,
                district_id=data.get('district', frontend_user.district_id),
                birthday=data.get('birthday', datetime(year=1995, month=7, day=15).date()),
                mobile_number=data.get('mobile_number', None),
                gender=data.get('gender', 2),
            )
            logging.getLogger('django.server').debug(f'user display name:{ user.display_name}')
            # 同步 头像
            if data['avatarUrl']:
                update_avatar_from_wx(
                    avatar_url=data['avatarUrl'],
                    frontend_user_id=user.id
                )
            user.synced_from_wx_at = datetime.now()
            user.is_synced_from_wx = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)


class PersonalCenterView(GenericViewSet):
    permission_classes = (IsFrontendUserPermission,)

    def get_serializer_class(self):
        if self.action == 'dashboard':
            return frontend_user_serializer.PersonalInfoSerializer
        if self.action == 'avatar':
            return frontend_user_serializer.UpdateAvatarSerializer
        if self.action == 'my':
            return frontend_user_serializer.UpdateFrontendUserSerializer
        return frontend_user_serializer.FrontendCurrentSerializer

    @action(methods=['get'], detail=False)
    def dashboard(self, request):
        """
        个人中心数据 fe-user-dashboard
        :param request:
        :return:
        """
        user = request.user.frontenduser
        joined_days = get_user_joined_days(date_joined=user.date_joined)
        user_info = frontend_user_serializer.PersonalInfoSerializer(instance=user)
        avatar = user.avatar
        media = Media.objects.filter(orig_file=avatar).first()
        media_serializer = MediaRefSerializer(
            media, context={'request': request}
        )
        user_data = user_info.data
        user_data['avatar'] = media_serializer.data
        order_info = get_front_user_status_statistics(front_user_id=user.id)
        coupon_info = get_front_user_count(frontend_user_id=user.id)
        data = {
            "user": user_data,
            "joined_days": joined_days,
            "order": order_info,
            "coupon": coupon_info,
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['post', 'patch'], detail=False)
    def avatar(self, request):
        """
        修改头像 fe-update-user-avatar
        :param request:
        :return:
        """
        user = request.user.frontenduser
        serializer = self.get_serializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'patch'], detail=False)
    def my(self, request):
        """
        修改基本信息 fe-update-user-profile
        :param request:
        :return:
        """
        frontend_user = request.user
        serializer = frontend_user_serializer.UpdateFrontendUserSerializer(instance=frontend_user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        error_dict = {}
        for k, v in serializer.errors.items():
            error_dict[k] = v[0]
        logging.getLogger('django.server').warning(f'serializer.errors:{serializer.errors}')
        return Response(error_dict, status=status.HTTP_400_BAD_REQUEST)


class WXAppShareCode(views.APIView):
    """
    获取小程序分享二维码 code mb-wxapp-detai
    """

    def get(self, request):
        merchant_id = self.request.merchant_id
        wx_mch_user_id = MerchantConfig.objects.get(merchant_id=merchant_id).wx_mch_user.id
        wxa_path = request.query_params['wxa_path']
        wxa_scene = request.query_params['wxa_scene']

        logger = logging.getLogger('django.server')
        logger.debug('--------------')
        logger.debug(wx_mch_user_id)
        logger.debug(wxa_path)
        logger.debug(wxa_scene)
        logger.debug('--------------')

        image_content,_ = get_wxa_code(mch_user_id=wx_mch_user_id, wxa_path=wxa_path, scene=wxa_scene)
        return HttpResponse(image_content, content_type='image/png')
