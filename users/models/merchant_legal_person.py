from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from b2c.misc.models import Media
from .merchant import Merchant


class MerchantLegalPerson(models.Model):
    """
    机构法人信息
    """

    realname = models.CharField(
        verbose_name='法人姓名', max_length=10, null=True, blank=True)

    idcard_number = models.CharField(
        verbose_name='身份证号', max_length=20, null=True, blank=True)

    idcard_valid_from = models.DateField(
        verbose_name='身份证有效期起始',
        null=True, blank=True)

    idcard_valid_to = models.DateField(
        verbose_name='身份证有效期结束',
        null=True, blank=True)

    idcard_front_image = GenericRelation(
        Media,
        verbose_name='身份证正面', null=True, blank=True)

    idcard_back_image = GenericRelation(
        Media,
        verbose_name='身份证反面', null=True, blank=True)

    merchant = models.OneToOneField(
        Merchant,
        on_delete=models.CASCADE,
        verbose_name='法人信息',
        related_name='legal_person'
    )

    class Meta:
        verbose_name_plural = verbose_name = "法人信息"

    def __str__(self):
        return self.realname
