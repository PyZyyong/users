from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions


class IsMerchantAdminPermission(permissions.BasePermission):
    """
    判断是否是商户管理员
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        from b2c.users.models import MerchantUser
        try:
            return request.user.merchantuser.is_merchant_admin
        except MerchantUser.DoesNotExist:
            return False


class IsFrontendUserPermission(permissions.BasePermission):
    """
    判断是否是frontend user
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        
        from b2c.users.models import FrontendUser
        try:
            return request.user.frontenduser.is_frontend_user
        except FrontendUser.DoesNotExist:
            return False


class IsMerchantUserPermission(permissions.BasePermission):
    """
    判断是否是merchant user
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        from b2c.users.models import MerchantUser
        try:
            return request.user.merchantuser.is_merchant_user
        except MerchantUser.DoesNotExist:
            return False
