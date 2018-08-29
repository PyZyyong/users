from django.db import transaction
from rest_framework import serializers

from b2c.misc.serializers import MediaRefSerializer
from b2c.users.models import Merchant, MerchantLegalPerson, MerchantCard
from b2c.users.services import (
    update_merchant_card,
    update_merchant_card_images,
    merchant_certificate_base_create,
    merchant_legal_person_create,
    update_merchant_certificate_images,
    update_idcard)


class MerchantSerializer(serializers.ModelSerializer):
    """
    Merchant
    """

    class Meta:
        model = Merchant
        fields = serializers.ALL_FIELDS


class MerchantWXAppSerializer(serializers.ModelSerializer):
    """
    Merchant wxapp
    """
    mch_id = serializers.CharField(source='config.wx_mch_user.mch_id')
    sign_key = serializers.CharField(source='config.wx_mch_user.sign_key')
    cert_pem = serializers.SerializerMethodField()
    key_pem = serializers.SerializerMethodField()

    class Meta:
        model = Merchant
        fields = ('mch_id', 'sign_key', 'cert_pem', 'key_pem')

    def get_cert_pem(self, obj):
        return obj.config.wx_mch_user.cert_pem.uuid

    def get_key_pem(self, obj):
        return obj.config.wx_mch_user.key_pem.uuid


class MerchantLegalPersonSerializer(serializers.ModelSerializer):
    """
    法人信息 认证
    """
    realname = serializers.CharField()
    idcard_number = serializers.CharField()
    idcard_valid_from = serializers.DateTimeField()
    idcard_valid_to = serializers.DateTimeField()
    idcard_front_image = serializers.FileField()
    idcard_back_image = serializers.FileField()

    class Meta:
        model = MerchantLegalPerson
        fields = ['realname',
                  'idcard_number',
                  'idcard_valid_from',
                  'idcard_valid_to',
                  'idcard_front_image',
                  'idcard_back_image'
                  ]

    def create(self, validated_data):
        print(validated_data)
        user = self.context['request'].user
        merchant_id = user.merchantuser.merchant.id
        return merchant_legal_person_create(
            merchant_id=merchant_id,
            realname=validated_data.get('realname', None),
            idcard_number=validated_data.get('idcard_number', None),
            idcard_valid_from=validated_data.get('idcard_valid_from', None),
            idcard_valid_to=validated_data.get('idcard_valid_to', None),
            idcard_front_image=validated_data.get('idcard_front_image', None),
            idcard_back_image=validated_data.get('idcard_back_image', None),
        )


class MerchantAuth1Serializer(serializers.ModelSerializer):
    """
    商户资质认证 基本信息 Auth1
    """
    merchant_legal_person = serializers.CharField(
        source='merchantlegalperson.realname',
        help_text='法人姓名')

    class Meta:
        model = Merchant
        fields = ['name', 'merchant_legal_person', 'district_province', 'district_city',
                  'district_area', 'address', 'owner', 'contact',
                  'contact_mobile_number', 'tel_phone', 'contact_email', 'contact_position', 'authenticated_state']

    # TODO 完善创建
    def create(self, validated_data):
        user = self.context['request'].user
        merchant_id = user.merchantuser.merchant.id
        return merchant_certificate_base_create(
            merchant_id=merchant_id,
            name=validated_data['name'],
            merchant_legal_person=validated_data['merchantlegalperson']['realname'],
            district_province=validated_data.get('district_province', None),
            district_city=validated_data.get('district_city', None),
            district_area=validated_data.get('district_area', None),
            address=validated_data.get('address', None),
            owner=validated_data.get('owner', None),
            contact=validated_data.get('contact', None),
            contact_mobile_number=validated_data.get('contact_mobile_number', None),
            tel_phone=validated_data.get('tel_phone', None),
            contact_email=validated_data.get('contact_email', None),
            contact_position=validated_data.get('contact_position', None),
            authenticated_state=validated_data.get('authenticated_state', None)
        )


class MerchantAuth2Serializer(serializers.Serializer):
    """
    商户资质认证 证书信息 Auth2
    """

    def create(self, validated_data):
        pass

    idcard_front_image = MediaRefSerializer(help_text='身份证正面')
    idcard_back_image = MediaRefSerializer(help_text='身份证反面')

    images = serializers.ListField(min_length=1,
                                   child=MediaRefSerializer())

    # TODO 完善创建
    @transaction.atomic
    def update(self, instance, validated_data):
        user = self.context['request'].user
        merchant = user.merchantuser.merchant
        merchant_legal_person = MerchantLegalPerson.objects.filter(merchant=merchant).first()
        # merchant_certificate = MerchantCertificate.objects.filter(merchant=merchant).first()
        idcard_front = validated_data.get('idcard_front_image', None)
        idcard_back = validated_data.get('idcard_back_image', None)
        images = validated_data.get('images', [])
        update_idcard(
            merchant_legal_person.id,
            idcard_front
        )
        update_idcard(
            merchant_legal_person.id,
            idcard_back
        )
        certificate = update_merchant_certificate_images(
            merchant_id=merchant.id,
            new_set=images
        )
        return certificate


class MerchantCardSerializer(serializers.ModelSerializer):
    """
     mb
     MerchantCard base + images
    """
    id = serializers.ReadOnlyField()
    address = serializers.CharField(
        source='merchant.address',
        help_text='详细地址',
    )
    contact_mobile_number = serializers.CharField(
        source='merchant.contact_mobile_number',
        help_text='联系电话',
    )

    class Meta:
        model = MerchantCard
        fields = ['id', 'description', 'contact_mobile_number', 'address', 'location_lat',
                  'location_lng']


class MerchantCardUpdateSerializer(serializers.ModelSerializer):
    """
    商户卡 更新
    """
    description = serializers.CharField(source='merchantcard.description')
    contact_mobile_number = serializers.CharField()
    location_lat = serializers.CharField(source='merchantcard.location_lat')
    location_lng = serializers.CharField(source='merchantcard.location_lng')
    address = serializers.CharField()
    images = serializers.ListField(child=MediaRefSerializer(), min_length=1, max_length=10)

    class Meta:
        model = MerchantCard
        fields = ['description', 'address', 'contact_mobile_number', 'location_lat', 'location_lng', 'images']

    @transaction.atomic
    def update(self, instance, validated_data):
        print(validated_data)
        merchant = instance
        # 基本信息
        merchant_card = validated_data.get('merchantcard', None)
        location_lat = merchant_card.get('location_lat', None) if merchant_card else None
        location_lng = merchant_card.get('location_lng', None) if merchant_card else None
        description = merchant_card.get('description', None) if merchant_card else None
        update_merchant_card(
            merchant_id=merchant.id,
            description=description,
            address=validated_data.get('address', None),
            location_lat=location_lat,
            contact_mobile_number=validated_data.get('contact_mobile_number', None),
            location_lng=location_lng
        )
        # media 信息
        update_merchant_card_images(
            merchant_id=instance.id,
            new_set=validated_data.get('images', []),
        )
        return instance

    def create(self, validated_data):
        pass
