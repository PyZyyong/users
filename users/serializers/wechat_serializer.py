from rest_framework import serializers

from b2c.misc.models.system_config import SystemConfig


class WeChatAuthCallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = ['wx_proxy_app_ticket', 'wx_proxy_app_ticket_expired_at', 'wx_proxy_app_token']
