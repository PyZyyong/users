from django.db import models

from b2c.general.base_model import BaseModel
from b2c.wxapp.models.wx_payment import WXPaymentOrder
from b2c.wxapp.models.wx_refund_state_type import WXRefundStateType


class WXOrderRefund(BaseModel):
    wx_order = models.OneToOneField(WXPaymentOrder, related_name='refund', on_delete=models.CASCADE)

    out_refund_no = models.CharField(
        max_length=255,
        verbose_name='商户退款单号'
    )

    refund_fee = models.IntegerField(
        null=True,
        verbose_name='退款金额'
    )

    refund_fee_type = models.CharField(
        max_length=255,
        null=True,
        verbose_name='货币种类'
    )

    refund_desc = models.CharField(
        max_length=255,
        null=True,
        verbose_name='退款原因'
    )

    refund_account = models.CharField(
        max_length=255,
        null=True,
        default='REFUND_SOURCE_RECHARGE_FUNDS',
        verbose_name='退款资金来源'
    )

    notify_url = models.CharField(
        max_length=255,
        null=True,
        verbose_name='退款结果通知url'
    )

    refund_id = models.CharField(
        max_length=255,
        null=True,
        verbose_name='微信退款单号'
    )

    cash_refund_fee = models.IntegerField(
        null=True,
        verbose_name='现金退款金额'
    )

    refund_recv_accout = models.CharField(
        max_length=255,
        null=True,
        verbose_name='退款入账账户'
    )

    refund_request_source = models.CharField(
        max_length=255,
        null=True,
        verbose_name='退款发起来源'
    )

    refund_status = models.IntegerField(
        choices=WXRefundStateType.choices(),
        default=WXRefundStateType.REFUNDCLOSE.value,
        null=True,
        verbose_name='退款状态'
    )

    settlement_refund_fee = models.IntegerField(
        null=True,
        verbose_name='退款金额'
    )

    success_time = models.DateTimeField(
        null=True,
        verbose_name='退款成功时间'
    )

    refund_success_time = models.DateTimeField(
        null=True,
        verbose_name='退款成功时间'
    )

    refund_channel = models.CharField(
        max_length=255,
        null=True,
        verbose_name='退款渠道'
    )

    return_code = models.CharField(
        max_length=255,
        null=True,
        verbose_name='返回状态码'
    )

    return_msg = models.CharField(
        max_length=255,
        null=True,
        verbose_name='返回信息'
    )

    result_code = models.CharField(
        max_length=255,
        null=True,
        verbose_name='业务结果'
    )

    err_code = models.CharField(
        max_length=255,
        null=True,
        verbose_name='错误代码'
    )

    err_code_des = models.CharField(
        max_length=255,
        null=True,
        verbose_name='错误代码描述'
    )

    def is_success(self):
        return 'SUCCESS' == self.return_code and 'SUCCESS' == self.result_code
