from django.db import models

from b2c.general.base_model import BaseModel
from b2c.wxapp.models.wx_mch_user import WXMchUser


class WXAppUser(BaseModel):
    """
    小程序用户
    """

    mch_user = models.ForeignKey(
        WXMchUser,
        on_delete=models.CASCADE
    )

    open_id = models.CharField(
        max_length=100,
        verbose_name='小程序用户唯一标识'
    )

    union_id = models.CharField(
        blank=True,
        null=True,
        max_length=100,
        verbose_name='同公众号主体下唯一标识'
    )

    session_key = models.CharField(
        max_length=255,
        verbose_name='密钥'
    )

    token = models.CharField(
        max_length=255,
        verbose_name='token'
    )

    nick_name = models.CharField(
        max_length=20,
        null=True,
        verbose_name='昵称'

    )
    avatar_url = models.CharField(
        max_length=255,
        null=True,
        verbose_name='头像'
    )
    gender = models.CharField(
        max_length=2,
        null=True,
        verbose_name='性别'
    )
    city = models.CharField(
        max_length=10,
        null=True,
        verbose_name='城市'
    )
    province = models.CharField(
        max_length=10,
        null=True,
        verbose_name='省份'
    )
    country = models.CharField(
        max_length=10,
        null=True,
        verbose_name='国家'
    )
    language = models.CharField(
        max_length=10,
        null=True,
        verbose_name='语言'
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        verbose_name='手机号'
    )
    pure_phone_number = models.CharField(
        max_length=20,
        null=True,
        verbose_name='区号的手机号'
    )
    country_code = models.CharField(
        max_length=5,
        null=True,
        verbose_name='区号'
    )
