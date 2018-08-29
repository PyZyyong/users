import hashlib
from datetime import datetime

from django.db import models

from django_fsm import transition, FSMIntegerField

from b2c.misc.models import District
from b2c.users.models.merchant_auth_status import MerchantAuthenticationState


class Merchant(models.Model):
    """
    机构信息
    """

    name = models.CharField(
        max_length=50,
        verbose_name="医院名称")

    name_code = models.CharField(
        verbose_name='英文名称',
        max_length=100,
        null=True,
        blank=True
    )

    district_province = models.ForeignKey(
        District,
        null=True,
        verbose_name="所在地(省)",
        related_name='district_as_merchant_provinces',
        on_delete=models.PROTECT
    )

    district_city = models.ForeignKey(
        District,
        null=True,
        verbose_name="所在地(市)",
        related_name='district_as_merchant_cities',
        on_delete=models.PROTECT
    )

    district_area = models.ForeignKey(
        District,
        null=True,
        verbose_name="所在地(区)",
        related_name='district_as_merchant_areas',
        on_delete=models.PROTECT
    )

    address = models.CharField(
        max_length=200,
        verbose_name='详细地址',
        null=True,
        blank=True
    )

    owner = models.CharField(
        null=True,
        blank=True,
        max_length=20,
        verbose_name='地推负责人'
    )
    contact = models.CharField(
        max_length=20,
        verbose_name="联系人"
    )

    tel_phone = models.CharField(
        max_length=20,
        verbose_name='固定电话',
        null=True,
        blank=True
    )
    contact_mobile_number = models.CharField(
        max_length=20,
        verbose_name="联系人电话"
    )
    contact_email = models.EmailField(
        max_length=50,
        verbose_name='联系人邮箱'
    )
    contact_position = models.CharField(
        null=True,
        blank=True,
        max_length=10,
        verbose_name='联系人职位'
    )
    authenticated_state = FSMIntegerField(
        choices=MerchantAuthenticationState.choices(),
        default=MerchantAuthenticationState.UNAUTHENTICATED.value
    )

    def save(self, *args, **kwargs):
        """
        create check name_code
        :param args:
        :param kwargs:
        :return:
        """
        salt = str(datetime.now().strftime("Y%m%d%H%M%S"))
        if not self.name_code:
            m = hashlib.md5((salt + str(self.id)).encode('utf-8'))\
                    .hexdigest().lower()
            name_code_db = Merchant.objects.filter(name_code=m[5:15])
            if not name_code_db:
                self.name_code = m[5:15]
            else:
                self.name_code = m[6:16]
        super(Merchant, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = verbose_name = "商户"

    def __str__(self):
        return self.name

    @transition(
        field='authenticated_state',
        source=[MerchantAuthenticationState.UNABLE_TO_AUTHENTICATE.value,
                MerchantAuthenticationState.UNAUTHENTICATED.value],
        target=MerchantAuthenticationState.AUTHENTICATED.value)
    def to_authenticate(self):
        pass

    @transition(
        field='authenticated_state',
        source=MerchantAuthenticationState.AUTHENTICATED.value,
        target=MerchantAuthenticationState.UNAUTHENTICATED.value)
    def to_unauthenticated(self):
        pass

    @transition(
        field='authenticated_state',
        source=MerchantAuthenticationState.UNAUTHENTICATED.value,
        target=MerchantAuthenticationState.UNABLE_TO_AUTHENTICATE.value)
    def to_unable_authenticated(self):
        pass
