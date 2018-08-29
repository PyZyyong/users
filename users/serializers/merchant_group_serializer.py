from django import db
from django.contrib.auth.models import Permission, Group
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db import transaction

from b2c.users.models import MerchantGroup
from b2c.users.services import create_merchant_group, update_merchant_group, merchant_group_del


def permissions_choice():
    """
    获取 权限 选项
    :return:
    """
    try:
        permissions_list = list(Permission.objects.all())
        new_list = []
        for permission in permissions_list:
            new_list.append(permission.codename)
        return new_list
    except db.utils.ProgrammingError:
        return []


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class GroupListSerializer(serializers.ModelSerializer):
    """
    所属商户 groups 不分页
    """
    id = serializers.IntegerField(source='group.id')
    name = serializers.CharField()

    class Meta:
        model = MerchantGroup
        fields = ['id', 'name']


class MerchantGroupListSerializer(serializers.ModelSerializer):
    """
    所属商户 groups
    """
    id = serializers.IntegerField()
    name = serializers.CharField()
    notes = serializers.CharField()
    created_at = serializers.CharField()
    updated_at = serializers.CharField()
    create_user = serializers.SerializerMethodField()
    permission_list = serializers.SerializerMethodField()

    def get_permission_list(self, obj):
        group = obj
        permissions = Permission.objects.filter(group__merchantgroup=group)
        data = PermissionSerializer(permissions, many=True)
        return data.data

    def get_create_user(self, obj):
        merchant_group = obj
        user = merchant_group.create_user
        return user.username

    class Meta:
        model = MerchantGroup
        fields = ['id', 'name', 'notes', 'created_at', 'updated_at', 'create_user', 'permission_list']


class MerchantGroupSerializer(serializers.Serializer):
    """
    MerchantGroup 绑定权限 创建、更新
    """
    name = serializers.CharField()
    notes = serializers.CharField(required=False)
    perms_code = serializers.MultipleChoiceField(
        choices=permissions_choice(),
        required=False,
        allow_empty=False,
    )

    class Meta:
        model = MerchantGroup
        fields = ['name', 'notes', 'perms_code']

    @transaction.atomic
    def update(self, instance, validated_data):
        merchant_group = instance
        print('merchant_group', merchant_group)
        print('validated_data', validated_data)
        merchant_group = update_merchant_group(
            merchant_group_id=merchant_group.id,
            name=validated_data.get('name', None),
            notes=validated_data.get('notes', None)
        )
        group = Group.objects.get(merchantgroup=merchant_group)
        codes = validated_data.get('perms_code', None)
        if codes:
            group.permissions.clear()
            perms = Permission.objects.filter(codename__in=codes)
            for i in perms:
                group.permissions.add(i)
            return merchant_group
        else:
            group.permissions.clear()
            return merchant_group

    @transaction.atomic
    def create(self, validated_data):
        print(validated_data)
        user = self.context['request'].user
        merchant = user.merchantuser.merchant
        merchant_group = create_merchant_group(
            name=validated_data['name'],
            user_id=user.id,
            merchant_id=merchant.id,
            notes=validated_data.get('notes', None)
        )
        group = Group.objects.get(merchantgroup=merchant_group)
        codes = validated_data.get('perms_code', None)
        if codes:
            perms = Permission.objects.filter(codename__in=codes)
            for i in perms:
                group.permissions.add(i)
            return merchant_group
        else:
            group.permissions.clear()
            return merchant_group


class MerchantGroupRetrieveSerializer(serializers.ModelSerializer):
    """
    Group + permissions retrieve
    """
    permission_list = serializers.SerializerMethodField()
    name = serializers.CharField()
    create_user = serializers.CharField()

    class Meta:
        model = MerchantGroup
        fields = ['id', 'name', 'created_at', 'updated_at', 'create_user', 'permission_list']

    def get_permission_list(self, obj):
        group = obj
        permissions = Permission.objects.filter(group__merchantgroup=group)
        data = PermissionSerializer(permissions, many=True)
        return data.data


class MerchantGroupDelSerializer(serializers.ModelSerializer):
    """
    Merchant Group del
    """
    def validate(self, data):
        msg = merchant_group_del(
                    merchant_group_id=self.instance.id
                )
        return msg

    class Meta:
        model = MerchantGroup
        fields = ['id']
