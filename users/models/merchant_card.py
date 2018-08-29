from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from b2c.misc.models import Media
from b2c.users.models import Merchant


class MerchantCard(models.Model):
    """
    商户卡（品牌）
    """
    merchant = models.OneToOneField(Merchant,
                                    on_delete=models.CASCADE,
                                    verbose_name='商户')
    description = models.CharField(max_length=2048,
                                   null=True,
                                   blank=True,
                                   verbose_name='介绍')
    location_lat = models.FloatField(verbose_name='地址纬度', null=True, blank=True)
    location_lng = models.FloatField(verbose_name='地址经度', null=True, blank=True)
    images = GenericRelation(Media, verbose_name='图册', null=True)

    class Meta:
        verbose_name_plural = verbose_name = '商户卡'

    def __str__(self):
        return self.merchant.name
