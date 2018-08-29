from enum import IntEnum

from datetime import datetime
from django.db import models
from django_fsm import FSMIntegerField

from b2c.misc.models import District
from b2c.users.models.user import User
from b2c.wxapp.models import WXAppUser
from b2c.general.interfaces import StatPageVisitor


class FrontendUserGender(IntEnum):
    """
    性别
    """
    FEMALE = 0
    MALE = 1
    UNKNOWN = 2

    @classmethod
    def choices(cls):
        return (
            (FrontendUserGender.FEMALE.value, '女'),
            (FrontendUserGender.MALE.value, '男'),
            (FrontendUserGender.UNKNOWN.value, '未知'),
        )


class FrontendUser(User, StatPageVisitor):
    """
    前端用户
    """
    birthday = models.DateField(
        verbose_name='生日',
        null=True,
        blank=True)

    wx_user = models.OneToOneField(
        WXAppUser, verbose_name='小程序用户',
        on_delete=models.PROTECT,
        null=True)

    merchant = models.ForeignKey(
        'users.Merchant',
        verbose_name='所属商户',
        on_delete=models.CASCADE)

    gender = FSMIntegerField(
        choices=FrontendUserGender.choices(),
        default=FrontendUserGender.UNKNOWN.value
    )
    is_synced_from_wx = models.BooleanField(
        verbose_name='是否从微信同步信息',
        default=False
    )
    synced_from_wx_at = models.DateTimeField(
        verbose_name='同步时间',
        null=True,
        blank=True
    )
    district = models.ForeignKey(
        District,
        verbose_name='常出没',
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return self.username
    
    @property
    def age(self):
        """
        :return:
        """
        if self.birthday:
            now = datetime.now().year
            age = now - self.birthday.year
            return age
        return 18

    class Meta:
        verbose_name_plural = verbose_name = "微信用户"

    @property
    def district_name(self):
        if not self.district_id:
            return ""
        if not self.district.parent_id:
            return self.district.name
        return "{0}-{1}".format(self.district.parent.name, self.district.name)

    def get_page_visitor_id(self):
        """
        获取ID
        :return:
        """
        return self.id

    def get_page_visitor_ip(self):
        """
        获取访问者IP
        :return:
        """
        return self.last_logged_in_ip if self.last_logged_in_ip else ""