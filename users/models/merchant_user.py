from django.db import models

from b2c.general.interfaces import SMSCodeReceiver
from b2c.users.models.merchant import Merchant
from b2c.users.models.user import User


class MerchantUser(User, SMSCodeReceiver):
    """
    Merchant User
    """
    merchant = models.ForeignKey(
        Merchant,
        related_name='merchant',
        on_delete=models.CASCADE,
        verbose_name='所属医院',
    )

    is_merchant_admin = models.BooleanField(
        default=False,
        verbose_name='是否是商户管理员'
    )

    notes = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        verbose_name="备注")

    def __str__(self):
        return self.username

    @property
    def sms_code_receiver_mobile_number(self):
        return self.mobile_number

    class Meta:
        verbose_name_plural = verbose_name = "医院用户"
        # codename , desc
        permissions = (
            ("mb_product_categories", "项目分类"),
            ("mb_all_products_list", "项目管理"),
            ("mb_products_recommended", "推荐项目"),
            ("mb_set_product_notice", "购买须知"),
            ("mb_order_list", "订单列表",),
            # ("mb_order_retrieve", "订单详情"),
            ("mb_coupons_operation", "优惠券"),
            ("mb_sales_operation", "秒杀"),
            ("mb_groupon_operation", "拼团"),
            ("mb_assistance_operation", "砍价"),
            ("mb_order_stat", "销售统计"),
            ("mb_daily_user_stat", "用户统计"),
            ("mb_activity_data_stat", "活动统计"),
            ("mb_finance_stat", "财务统计"),
            ("mb_reservation_stat", "服务统计"),
            ("mb_index_page_banner", "首页banner"),
            # ("mb_merchant_certificate", "企业认证"),
            # ("mb_set_sms_sign", "短信签名"),
            ("mb_merchant_user_manage", "人员管理"),
            ("mb_merchant_index_page", "商户主页"),
            ("mb_merchant_card", "医院品牌"),
            ("mb_binding_wx_applet", "小程序绑定"),
            ("mb_wx_pay_auth", "微信支付授权"),
            ("mb_merchant_user_set_group", "角色管理")
        )
