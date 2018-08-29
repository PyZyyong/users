from django.db import models
from django.contrib.auth.models import Group

from b2c.general.base_model import BaseModel
from .merchant import Merchant
from .user import User


class MerchantGroup(BaseModel):
    """
    机构 用户组
    """
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        verbose_name='商户组'
    )
    
    merchant = models.ForeignKey(
        Merchant,
        related_name='merchant_group',
        on_delete=models.CASCADE,
        verbose_name='所属商户',
    )
    name = models.CharField(
        verbose_name='组名',
        max_length=50
    )
    
    create_user = models.ForeignKey(
        User,
        related_name='create_user',
        on_delete=models.CASCADE,
        verbose_name='创建者',
        null=True
    )
    notes = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        verbose_name="备注")
    
    def __str__(self):
        return self.group.name
    
    class Meta:
        verbose_name_plural = verbose_name = "商户组"
