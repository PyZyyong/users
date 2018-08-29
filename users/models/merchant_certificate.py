from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from b2c.misc.models import Media
from .merchant import Merchant


class MerchantCertificate(models.Model):
    """
    资质证书
    """
    name = models.CharField(
        max_length=20, verbose_name='名称', null=True, blank=True)
    codename = models.CharField(
        max_length=50, verbose_name='编码', null=True, blank=True)
    no = models.CharField(
        max_length=50, verbose_name='证书编号', null=True, blank=True)
    extra_data1 = models.CharField(
        max_length=100, verbose_name='额外信息', null=True, blank=True)
    valid_from = models.DateField(
        verbose_name='许可证有效期起始',
        null=True, blank=True, default='')

    valid_to = models.DateField(
        verbose_name='许可证有效期结束',
        null=True, blank=True, default='')

    front_img = GenericRelation(
        Media,
        verbose_name='许可证图片正面', null=True)

    back_img = GenericRelation(
        Media,
        verbose_name='许可证图片反面', null=True)

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        verbose_name='资质证书',
        related_name='certificates'
    )

    class Meta:
        verbose_name_plural = verbose_name = "资质证书"

    def __str__(self):
        return self.name
