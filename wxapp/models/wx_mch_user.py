from django.db import models

from b2c.general.base_model import BaseModel
from b2c.wxapp.models.wx_app_review_state_type import WXAppReviewStateType
from b2c.wxapp.models.wx_mch_cert_type import WXMchCertType


class WXMchUser(BaseModel):
    """
    小程序商家用户
    """

    app_id = models.CharField(
        max_length=100,
        null=True,
        verbose_name='小程序id'
    )

    app_secret = models.CharField(
        null=True,
        max_length=100,
        verbose_name='小程序密钥'
    )

    mch_id = models.CharField(
        null=True,
        max_length=255,
        verbose_name='商户id'
    )

    access_token = models.CharField(
        null=True,
        max_length=255,
        verbose_name='接口调用凭证'
    )

    refresh_token = models.CharField(
        null=True,
        max_length=255,
        verbose_name='授权刷新凭证'
    )

    expires_in = models.IntegerField(
        default=0,
        verbose_name='凭证有效时间'
    )

    token_refresh_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="access_token凭证更新时间"
    )

    sign_key = models.CharField(
        null=True,
        max_length=255,
        verbose_name='签名算法key'
    )

    app_review_status = models.IntegerField(
        choices=WXAppReviewStateType.choices(),
        null=True,
        verbose_name='小程序审核状态'
    )

    app_review_result = models.CharField(
        null=True,
        max_length=255,
        verbose_name='小程序审核结果'
    )

    app_version = models.CharField(
        null=True,
        max_length=255,
        verbose_name='小程序版本'
    )

    app_submitted_at = models.DateTimeField(
        null=True,
        verbose_name='小程序提交时间'
    )

    app_reviewed_at = models.DateTimeField(
        null=True,
        verbose_name='小程序审核时间'
    )

    @property
    def cert_pem(self):
        return self.apiclient_certs.filter(
            cert_type=WXMchCertType.CERT_PEM.value).first().certs.first()

    @property
    def key_pem(self):
        return self.apiclient_certs.filter(
            cert_type=WXMchCertType.KEY_PEM.value).first().certs.first()

    @property
    def cert_pem_file(self):
        return self.cert_pem.orig_file.file.name

    @property
    def key_pem_file(self):
        return self.key_pem.orig_file.file.name

    class Meta:
        verbose_name_plural = verbose_name = "小程序商家用户"

    def __str__(self):
        return self.app_id
