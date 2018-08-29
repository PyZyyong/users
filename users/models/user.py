from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from b2c.general.interfaces import ReminderSubscriber
from b2c.misc.models import Media


class User(AbstractUser, ReminderSubscriber):
    """
    系统用户
    """

    _avatar = GenericRelation(
        Media,
        verbose_name='头像',
    )

    updated_at = models.DateTimeField(
        verbose_name='最后更新时间',
        auto_now=True,
    )

    last_logged_in_ip = models.CharField(
        verbose_name='最后登录IP',
        null=True,
        blank=True,
        max_length=20
    )

    mobile_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="手机号")

    display_name = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='昵称 or 姓名'
    )

    is_admin_user = models.BooleanField(
        default=False,
        verbose_name='是否是管理员用户'
    )

    is_merchant_user = models.BooleanField(
        default=False,
        verbose_name='是否是医院用户',
    )

    is_frontend_user = models.BooleanField(
        default=False,
        verbose_name='是否是微信用户',
    )

    @property
    def avatar(self):
        """
        返回头像
        :return:
        """
        return self._avatar.first().orig_file if self._avatar.first() else None

    def get_reminder_subscriber_name(self):
        """
        获取订阅者的名称
        :return:
        """
        return self.display_name or self.username

    def get_reminder_subscriber_id(self):
        """
        获取ID
        :return:
        """
        return self.id

    def get_reminder_subscriber_mobile_number(self):
        """
        获取电话
        :return:
        """
        return self.mobile_number

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = verbose_name = "用户"
