from rest_framework import serializers

from b2c.wxapp.models.wx_payment import WXPaymentOrder


class WXOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WXPaymentOrder
        fields = serializers.ALL_FIELDS
