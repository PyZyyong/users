from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_jwt.serializers import JSONWebTokenSerializer, jwt_payload_handler, jwt_encode_handler

from b2c.misc.sms_service import SMSService
from b2c.users.models import User, MerchantUser
from b2c.users.serializers.merchant_group_serializer import PermissionSerializer,\
    GroupSerializer
from b2c.users.services import create_merchant_user, update_merchant_user, user_enable, user_disable


class UserLoginSerializer(JSONWebTokenSerializer):
    """
    用户登陆获取JWT serializer
    """

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError('账号已冻结，无法登陆')

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    当前登录用户信息
    """
    merchant_name = serializers.SerializerMethodField()
    merchant_name_code = serializers.SerializerMethodField()
    merchant_id = serializers.SerializerMethodField()
    merchant_admin_mobile = serializers.SerializerMethodField()
    notes = serializers.CharField(source='merchantuser.notes')
    merchant_wx_authenticated = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    def get_merchant_admin_mobile(self, obj):
        merchant = obj.merchantuser.merchant
        merchant_admin = MerchantUser.objects.filter(
            merchant=merchant,
            is_merchant_admin=True).first()
        try:
            mobile = merchant_admin.mobile_number
        except AttributeError:
            mobile = None
        return mobile

    def get_merchant_name(self, obj):
        user = obj
        return user.merchantuser.merchant.name

    def get_merchant_name_code(self, obj):
        user = obj
        return user.merchantuser.merchant.name_code

    def get_merchant_id(self, obj):
        user = obj
        return user.merchantuser.merchant.id

    def get_merchant_wx_authenticated(self, obj):
        user = obj
        merchant = user.merchantuser.merchant
        try:
            config = merchant.config
            if config.wx_mch_user is None:
                return False
        except AttributeError:
            return False
        return True

    def get_permissions(self, obj):
        user = obj
        # permissions = user.get_all_permissions()
        permissions = user.get_group_permissions()
        permissions_list = []
        for permission in permissions:
            perm = permission.split('.')[1]
            try:
                permission = Permission.objects.get(codename=perm)
                permissions_list.append(permission)
            except Permission.DoesNotExist:
                pass
        data = PermissionSerializer(permissions_list, many=True)
        return data.data

    class Meta:
        model = MerchantUser
        fields = [
            'merchant_name', 'merchant_id', 'merchant_name_code', 'merchant_admin_mobile',
            'merchant_wx_authenticated', 'username', 'mobile_number', 'display_name', 'email',
            'is_active', 'notes', 'permissions']


class MerchantUserListSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = MerchantUser
        fields = ['id', 'username', 'mobile_number', 'display_name', 'email', 'is_active',
                  'is_merchant_admin' ,'notes', 'date_joined', 'is_merchant_admin', 'groups']

    def get_groups(self, obj):
        user = obj
        groups = user.groups.first()
        serializer = GroupSerializer(groups)
        return serializer.data


class MerchantUserCreateSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    mobile_number = serializers.CharField(required=True, help_text='电话')
    display_name = serializers.CharField(required=True, help_text='姓名')
    group = serializers.IntegerField(required=True, help_text='角色', write_only=True)

    class Meta:
        model = MerchantUser
        fields = ['mobile_number', 'display_name', 'group']

    def create(self, validated_data):
        user = self.context['request'].user
        merchant = user.merchantuser.merchant
        number = User.objects.filter(mobile_number=validated_data['mobile_number'])
        if number:
            raise serializers.ValidationError('该手机号已被注册！')
        merchant_user = create_merchant_user(
                    username=validated_data['mobile_number'],
                    mobile_number=validated_data['mobile_number'],
                    display_name=validated_data['display_name'],
                    is_merchant_admin=False,
                    merchant_id=merchant.id,
                    is_active=False,
                    is_admin_user=False,
                    is_merchant_user=True,
                    is_frontend_user=False,
                    )
        if merchant_user:
            group = Group.objects.filter(id=validated_data.get('group', None)).first()
            merchant_user.groups.add(group)
            merchant_user.save()
            # TODO login_url 换成线上环境地址
            content = "[{merchant_name}]管理员已为您添加账号，请点击前往{login_url}，进行账号激活。" \
                .format(
                    merchant_name=merchant.config.sms_sign if merchant.config.sms_sign else merchant.name,
                    login_url='https://elk.yimeijian.cn/v1/mb/users/verify_login_sms_code/'
                )
            SMSService.send_text(phone=merchant_user.mobile_number, content=content)
        return merchant_user


class MerchantUserSerializer(serializers.Serializer):
    """
    MerchantUser Serializer
    """
    password = serializers.CharField(write_only=True,
                                     style={'input_type': 'password'})
    email = serializers.EmailField(
        allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message="邮箱已经存在!")])
    mobile_number = serializers.CharField(
        allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message="手机号已被使用!")])
    notes = serializers.CharField(source='merchantuser.notes')

    class Meta:
        model = MerchantUser
        fields = ['username', 'mobile_number', 'display_name', 'email', 'is_active',
                  'password', 'notes', 'is_merchant_admin']

    def update(self, instance, validated_data):
        user = instance
        return update_merchant_user(
                    user_id=user.id,
                    is_active=validated_data['is_active'],
                    is_admin_user=False,
                    is_merchant_user=True,
                    is_frontend_user=False,
                    username=validated_data['username'],
                    mobile_number=validated_data['mobile_number'],
                    email=validated_data['email'],
                    display_name=validated_data['display_name'],
                    notes=validated_data['merchantuser']['notes'],
                    )
    
    def create(self, validated_data):
        pass


class MerchantUserRetrieveSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    class Meta:
        model = MerchantUser
        fields = ['username', 'mobile_number', 'display_name', 'email', 'notes',
                  'is_active', 'group']

    def get_group(self, obj):
        """
        get user groups
        :param obj:
        :return:
        """
        try:
            group = Group.objects.filter(user=obj).values('id', 'name').first()
            return group
        except Exception as e:
            return None


class MerchantEnableSerializer(serializers.Serializer):
    """
    商户用户 启用
    """

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        user = instance
        if user.is_active is True:
            raise serializers.ValidationError("账户已激活")
        return user_enable(
            user_id=user.id
        )


class MerchantDisableSerializer(serializers.Serializer):
    """
    商户用户 禁用
    """

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        user = instance
        if user.is_active is False:
            raise serializers.ValidationError("账户已冻结！")
        return user_disable(
            user_id=user.id
        )
