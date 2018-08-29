from django.contrib import admin

from .models import WXMchUser
from b2c.users.models.merchant_config import MerchantConfig


class WXMchUserAdmin(admin.ModelAdmin):
    """
    小程序商户表显示
    """
    list_display = ['merchant', 'app_id', 'app_review_status', 'app_review_result', 'app_version', 'app_submitted_at',
                    'app_reviewed_at', 'access_token', 'refresh_token']
    search_fields = ['app_id', 'app_review_status', 'app_review_result', 'app_version', 'app_submitted_at',
                     'app_reviewed_at']
    list_filter = ['app_id', 'app_review_status', 'app_review_result', 'app_version', 'app_submitted_at',
                   'app_reviewed_at']

    def merchant(self, obj):
        config = MerchantConfig.objects.filter(wx_mch_user=obj).first()
        if config:
            return config.merchant
        return ''


admin.site.register(WXMchUser, WXMchUserAdmin)
