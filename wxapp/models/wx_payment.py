from django.db import models

from b2c.general.base_model import BaseModel
from b2c.wxapp.models.wx_app_user import WXAppUser
from b2c.wxapp.models.wx_mch_user import WXMchUser
from b2c.wxapp.models.wx_trade_state_type import WXTradeStateType


class WXPaymentOrder(BaseModel):
    mch_user = models.ForeignKey(WXMchUser, on_delete=models.CASCADE)
    app_user = models.ForeignKey(WXAppUser, on_delete=models.CASCADE)

    nonce_str = models.CharField(
        max_length=255,
        verbose_name='随机字符串'
    )

    sign = models.CharField(
        max_length=255,
        verbose_name='签名'
    )

    body = models.CharField(
        max_length=255,
        verbose_name='商品描述'
    )

    out_trade_no = models.CharField(
        max_length=255,
        verbose_name='商户订单号'
    )

    total_fee = models.IntegerField(
        verbose_name='标价金额'
    )

    spbill_create_ip = models.CharField(
        max_length=255,
        verbose_name='终端IP'
    )

    notify_url = models.CharField(
        max_length=255,
        verbose_name='通知地址'
    )

    trade_type = models.CharField(
        max_length=255,
        default='JSAPI',
        verbose_name='交易类型'
    )

    trade_state = models.IntegerField(
        choices=WXTradeStateType.choices(),
        default=WXTradeStateType.NOTPAY.value,
        null=True,
        verbose_name='交易状态'
    )

    sign_type = models.CharField(
        max_length=255,
        null=True,
        verbose_name='签名类型'
    )

    device_info = models.CharField(
        max_length=255,
        null=True,
        verbose_name='设备号'
    )

    detail = models.CharField(
        max_length=255,
        null=True,
        verbose_name='商品详情'
    )

    attach = models.CharField(
        max_length=255,
        null=True,
        verbose_name='附加数据'
    )

    fee_type = models.CharField(
        max_length=255,
        null=True,
        default='CNY',
        verbose_name='标价币种'
    )

    time_start = models.DateTimeField(
        null=True,
        verbose_name='交易起始时间'
    )

    time_expire = models.DateTimeField(
        null=True,
        verbose_name='交易结束时间'
    )

    goods_tag = models.CharField(
        max_length=255,
        null=True,
        verbose_name='订单优惠标记'
    )

    limit_pay = models.CharField(
        max_length=255,
        null=True,
        verbose_name='指定支付方式'
    )
    product_id = models.CharField(
        max_length=255,
        null=True,
        verbose_name='商品ID'
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

    prepay_id = models.CharField(
        max_length=255,
        null=True,
        verbose_name='预支付标识'
    )

    prepay_refresh_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="prepay_id 刷新时间"
    )

    code_url = models.CharField(
        max_length=255,
        null=True,
        verbose_name='二维码地址'
    )

    is_subscribe = models.CharField(
        max_length=255,
        null=True,
        verbose_name='是否关注公众账号'
    )

    bank_type = models.CharField(
        max_length=255,
        null=True,
        verbose_name='付款银行'
    )

    settlement_total_fee = models.IntegerField(
        null=True,
        verbose_name='应结订单金额'
    )

    cash_fee = models.IntegerField(
        null=True,
        verbose_name='现金支付金额'
    )

    cash_fee_type = models.CharField(
        max_length=255,
        null=True,
        verbose_name='现金支付货币类型'
    )

    transaction_id = models.CharField(
        max_length=255,
        null=True,
        verbose_name='微信支付订单号'
    )

    time_end = models.CharField(
        max_length=255,
        null=True,
        verbose_name='支付完成时间'
    )

    def is_success(self):
        return 'SUCCESS' == self.return_code and 'SUCCESS' == self.result_code
