from rest_framework import serializers

from b2c.wxapp.models.wx_mch_user import WXMchUser


class WXOAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = WXMchUser
        fields = serializers.ALL_FIELDS
