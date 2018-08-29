from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from b2c.misc.models import District, Media
from b2c.misc.serializers import MediaRefSerializer
from b2c.users.models import FrontendUser
from b2c.users.services import update_frontend_user, update_avatar
from b2c.wxapp.models import WXAppUser


class WxUserSerializer(ModelSerializer):

    class Meta:
        model = WXAppUser
        fields = serializers.ALL_FIELDS


class FrontendCurrentSerializer(ModelSerializer):
    username = serializers.CharField()
    display_name = serializers.CharField()
    birthday = serializers.DateField()
    gender = serializers.CharField()
    mobile_number = serializers.CharField()
    merchant = serializers.SerializerMethodField()

    def get_merchant(self, obj):
        return obj.merchant.name

    class Meta:
        model = FrontendUser
        fields = ['username', 'display_name', 'birthday', 'gender', 'mobile_number',
                  'merchant']


class PersonalInfoSerializer(serializers.ModelSerializer):
    """
    微信 个人信息
    """
    class Meta:
        model = FrontendUser
        fields = ['display_name', 'gender', 'birthday', 'mobile_number',
                  'district', 'date_joined', 'avatar']
    display_name = serializers.CharField()
    gender = serializers.CharField()
    birthday = serializers.CharField()
    mobile_number = serializers.CharField()
    date_joined = serializers.DateTimeField()
    district = serializers.SerializerMethodField()

    def get_district(self, obj):
        address = obj.district
        if address:
            if address.parent_id:
                parent = District.objects.get(code_name=address.parent_id)
                if parent.parent_id:
                    parent_parent = District.objects.get(code_name=parent.parent_id)
                    return parent_parent.name, parent.name, address.name
                return parent.name, address.name
            return address.name
        return None


class UpdateAvatarSerializer(serializers.ModelSerializer):
    """
    frontend user 头像
    """
    avatar = MediaRefSerializer(help_text='微信头像')

    def update(self, instance, validated_data):
        user = instance
        update_avatar(
               user_id=user.id,
               uuid=validated_data['avatar']
        )
        return instance

    class Meta:
        model = FrontendUser
        fields = ['avatar']


class UpdateFrontendUserSerializer(serializers.ModelSerializer):
    """
    frontend user 基本信息
    """
    class Meta:
        model = FrontendUser
        fields = ['display_name', 'gender', 'birthday', 'mobile_number',
                  'last_login', 'district']
    display_name = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.IntegerField(required=False)
    birthday = serializers.CharField(required=False, allow_blank=True)
    district = serializers.CharField(required=False, allow_blank=True)
    mobile_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_login = serializers.DateTimeField(required=False)

    def update(self, instance, validated_data):
        print(validated_data)
        frontend_user = instance

        district_name = validated_data.get('district', None)
        if district_name:
            district_object = District.objects.filter(name__icontains=district_name[0:2]).first()
        else:
            district_object = None
        frontend_user = update_frontend_user(
                    frontend_user_id=frontend_user.id,
                    username=frontend_user.username,
                    birthday=validated_data.get('birthday', None),
                    mobile_number=frontend_user.mobile_number,
                    display_name=validated_data.get('display_name', None),
                    gender=validated_data.get('gender', frontend_user.frontenduser.gender),
                    district_id=district_object.id if district_object else None,
                    is_admin_user=False,
                    is_merchant_user=False,
                    is_frontend_user=True,
                )
        frontend_user.save()
        return frontend_user


class FrontendUserAvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        image = obj._avatar.first()
        serializer = MediaRefSerializer(image, context=self.context)
        return serializer.data

    class Meta:
        model = FrontendUser
        fields = ('id', 'avatar','display_name')