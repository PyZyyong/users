# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.models import Permission

# from .models import User
from .models import AdminUser
from .models import MerchantUser
from .models import FrontendUser
from .models import Merchant
from .models import MerchantCard
from .models import MerchantCertificate
from .models import MerchantConfig
from .models import MerchantLegalPerson
from .models import MerchantGroup
from b2c.misc.models.district import District
from b2c.users.services import create_merchant_group


class UserAdmin(admin.ModelAdmin):
    """
    用户表显示
    """
    list_display = ['display_name', 'mobile_number', 'email', 'date_joined']
    search_fields = ['display_name', 'mobile_number', 'email']
    list_filter = ['display_name', 'mobile_number', 'email', 'date_joined']


class MerchantAdmin(admin.ModelAdmin):
    """
    商户表显示
    """
    list_display = ['name', 'province', 'city', 'owner', 'contact', 'contact_mobile_number',
                    'authenticated_state']
    search_fields = ['name', 'district_province', 'owner', 'contact', 'contact_mobile_number', 'authenticated_state']
    list_filter = ['name', 'district_province', 'owner', 'contact', 'contact_mobile_number', 'authenticated_state']

    def province(self, obj):
        district = District.objects.filter(pk=obj.pk).first()
        if district:
            return district.name
        return ''

    def city(self, obj):
        district = District.objects.filter(pk=obj.pk).first()
        if district:
            return district.name
        return ''

    def save_model(self, request, obj, form, change):
        super(MerchantAdmin, self).save_model(request, obj, form, change)
        if not change:
            merchant_id = self.model.objects.get(pk=obj.pk).id
            merchant_group = create_merchant_group(merchant_id=merchant_id, name='财务', notes='可查看销售数据')
            permission = Permission.objects.get(codename='mb_order_list')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_order_stat')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_finance_stat')
            merchant_group.group.permissions.add(permission)

            merchant_group = create_merchant_group(merchant_id=merchant_id, name='活动企划',
                                                   notes='负责活动运营，查看活动数据')
            permission = Permission.objects.get(codename='mb_coupons_operation')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_sales_operation')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_groupon_operation')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_assistance_operation')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_order_stat')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_activity_data_stat')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_index_page_banner')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_merchant_card')
            merchant_group.group.permissions.add(permission)

            merchant_group = create_merchant_group(merchant_id=merchant_id, name='网络运营', notes='负责管理项目')
            permission = Permission.objects.get(codename='mb_product_categories')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_all_products_list')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_products_recommended')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_set_product_notice')
            merchant_group.group.permissions.add(permission)

            merchant_group = create_merchant_group(merchant_id=merchant_id, name='电商咨询师',
                                                   notes='客服，可查看订单，对订单进行相应操作')
            permission = Permission.objects.get(codename='mb_order_list')
            merchant_group.group.permissions.add(permission)
            permission = Permission.objects.get(codename='mb_reservation_stat')
            merchant_group.group.permissions.add(permission)

            merchant_group = create_merchant_group(merchant_id=merchant_id, name='营销/市场总监',
                                                   notes='子管理员权限，可使用全部功能')
            permissions = Permission.objects.all()
            for permission in permissions:
                merchant_group.group.permissions.add(permission)


class MerchantCardAdmin(admin.ModelAdmin):
    """
    商户配置显示
    """
    list_display = ['merchant', 'description', 'location_lat', 'location_lng', 'images']
    search_fields = ['merchant', 'description']
    list_filter = ['merchant', 'description']


class MerchantCertificateAdmin(admin.ModelAdmin):
    """
    商户证书显示
    """
    list_display = ['name', 'codename', 'no', 'extra_data1', 'valid_from', 'valid_to', 'front_img', 'back_img',
                    'merchant']
    search_fields = ['name', 'codename', 'no']
    list_filter = ['name', 'codename', 'no', ]


class MerchantConfigAdmin(admin.ModelAdmin):
    """
    商户配置显示
    """
    list_display = ['merchant', 'sms_sign', 'wx_mch_user']
    search_fields = ['merchant', 'sms_sign', 'wx_mch_user']
    list_filter = ['merchant', 'sms_sign', 'wx_mch_user']


class MerchantLegalPersonAdmin(admin.ModelAdmin):
    """
    机构法人信息显示
    """
    list_display = ['merchant', 'realname', 'idcard_number', 'idcard_valid_from', 'idcard_valid_to',
                    'idcard_front_image', 'idcard_back_image']
    search_fields = ['merchant', 'realname', 'idcard_number']
    list_filter = ['merchant', 'realname', 'idcard_number', 'idcard_valid_from', 'idcard_valid_to']


class MerchantGroupAdmin(admin.ModelAdmin):
    """
    机构用户组显示
    """
    list_display = ['merchant', 'group', 'name', 'create_user', 'notes']
    search_fields = ['merchant', 'group', 'name', 'create_user', 'notes']
    list_filter = ['merchant', 'group', 'name', 'create_user', 'notes']


# admin.site.unregister(User)
admin.site.register(AdminUser, UserAdmin)
admin.site.register(MerchantUser, UserAdmin)
admin.site.register(FrontendUser, UserAdmin)
admin.site.register(Merchant, MerchantAdmin)
admin.site.register(MerchantCard, MerchantCardAdmin)
admin.site.register(MerchantCertificate, MerchantCertificateAdmin)
admin.site.register(MerchantConfig, MerchantConfigAdmin)
admin.site.register(MerchantLegalPerson, MerchantLegalPersonAdmin)
admin.site.register(MerchantGroup, MerchantGroupAdmin)
