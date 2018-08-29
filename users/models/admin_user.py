from django.db import models

from b2c.users.models.user import User


class AdminUser(User):
    """
    Admin User
    """

    YMJ_OPEN_CENTER = 1
    LDAP = 2
    INTERNAL = 3
    SOURCE_CHOICE = (
        (YMJ_OPEN_CENTER, 'YMJ'),
        (LDAP, 'LDAP'),
        (INTERNAL, '内部创建'),
    )

    source = models.CharField(
        choices=SOURCE_CHOICE,
        default=INTERNAL,
        max_length=50,
        verbose_name='用户来源'
    )

    # 记录 ldap账号登录后获取 该账号所属部门 Admin user
    department_description = models.CharField(
        null=True,
        blank=True,
        max_length=20,
        verbose_name="所属部门")

    notes = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        verbose_name="备注")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = verbose_name = "Admin用户"
