from rest_framework import serializers

from b2c.users.models import Merchant, MerchantCard


class MerchantSerializer(serializers.ModelSerializer):
    """
    Merchant
    """
    class Meta:
        model = Merchant
        fields = serializers.ALL_FIELDS


class MerchantCardSerializer(serializers.ModelSerializer):
    """
    MerchantCard info
    """
    merchant = serializers.SerializerMethodField()
    address = serializers.CharField(
        source='merchant.address',
        help_text='详细地址',
    )
    tel_phone = serializers.CharField(
        source='merchant.tel_phone',
        help_text='联系电话',
    )

    def get_merchant(self, obj):
        print(isinstance(obj, MerchantCard))
        return obj.merchant.name

    class Meta:
        model = MerchantCard
        fields = ['merchant', 'tel_phone', 'address', 'description',
                  'location_lat', 'location_lng']
