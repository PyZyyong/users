from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from b2c.general.base_model import BaseModel
from b2c.misc.models import Media
from b2c.wxapp.models import WXMchUser
from b2c.wxapp.models.wx_mch_cert_type import WXMchCertType


class WXMchCert(BaseModel):
    """
    商户证书
    """
    mch_user = models.ForeignKey(
        WXMchUser,
        on_delete=models.CASCADE,
        verbose_name='商户',
        related_name='apiclient_certs'
    )

    cert_type = models.SmallIntegerField(
        choices=WXMchCertType.choices(),
        blank=True,
        null=True,
        verbose_name='证书类型')

    certs = GenericRelation(Media, verbose_name='证书')
