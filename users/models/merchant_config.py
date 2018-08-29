from django.db import models

from b2c.users.models import Merchant
from b2c.wxapp.models import WXMchUser


class MerchantConfig(models.Model):
    """
    商户配置
    """
    merchant = models.OneToOneField(Merchant,
                                    verbose_name='所属商家',
                                    on_delete=models.CASCADE,
                                    related_name="config")
    shop_name = models.CharField(verbose_name='商铺名称',
                                 null=True, blank=True,
                                 max_length=100)
    sms_sign = models.CharField(max_length=20,
                                verbose_name='短信签名',
                                null=True,
                                blank=True)
    wx_mch_user = models.OneToOneField(WXMchUser,
                                       verbose_name='所属微信小程序商户',
                                       on_delete=models.PROTECT, null=True)
