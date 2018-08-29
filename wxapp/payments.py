import datetime
from datetime import timedelta

from django.conf import settings

from b2c.general.interfaces import PaymentAdapter, PaymentState
from b2c.wxapp.models import WXPaymentOrder
from b2c.wxapp.models.wx_trade_state_type import WXTradeStateType
from b2c.wxapp.services import wx_order_create, get_wx_pay_params, wx_order_trade_state_update, parse_pay_notify


class WeChatPaymentAdapter(PaymentAdapter):
    """
    微信支付
    """

    @property
    def payment_state(self):
        """
        返回支付状态
        :return:
        """
        payment_state_mapping = {
            WXTradeStateType.USERPAYING: PaymentState.PAYING,
            WXTradeStateType.NOTPAY: PaymentState.PAYING,
            WXTradeStateType.REVOKED: PaymentState.PAYING,
            WXTradeStateType.SUCCESS: PaymentState.SUCCESS,
            WXTradeStateType.PAYERROR: PaymentState.FAILED,
            WXTradeStateType.CLOSED: PaymentState.FAILED,
        }
        wx_order = WXPaymentOrder.objects.get(out_trade_no=self.order.sn)
        try:
            return payment_state_mapping.get(WXTradeStateType(wx_order.trade_state))
        except WXPaymentOrder.DoesNotExist:
            raise ValueError('微信无此订单：{}'.format(self.order.sn))

    def _request_payment(self):
        """
        发起微信支付
        :return:
        """
        now = datetime.datetime.now()
        try:
            wx_order = WXPaymentOrder.objects.get(out_trade_no=self.order.sn)
        except WXPaymentOrder.DoesNotExist:
            creator = self.order.creator
            label = f'{creator.merchant.name}-{self.order.products.first().title}'

            callback_url = f'{settings.WX_CALLBACK_DOMAIN}/v1/ab/wechat_payment/result/'
            wx_order = wx_order_create(
                app_user_id=creator.wx_user.id,
                mch_user_id=creator.wx_user.mch_user.id,
                trade_type="JSAPI",
                body=label,
                total_fee=int(self.order.total_amount * 100),
                notify_url=callback_url,
                out_trade_no=self.order.sn,
                client_ip=creator.last_logged_in_ip,
                time_start=now,
                time_expire=self.order.expired_at - timedelta(seconds=30),
            )

        return get_wx_pay_params(wx_order.id)

    def _cancel_payment(self):
        pass

    def _process_new_state(self, wx_order):
        # 通知状态变更
        if wx_order.trade_state == WXTradeStateType.SUCCESS.value:
            self._notify_state_change(new_state=PaymentState.SUCCESS, old_state=PaymentState.PAYING)
        elif wx_order.trade_state == WXTradeStateType.PAYERROR.value:
            self._notify_state_change(new_state=PaymentState.FAILED, old_state=PaymentState.PAYING)
        else:
            # TODO 处理其他 wx_order.trade_state
            raise ValueError('无法处理的微信支付状态：{}'.format(wx_order.trade_state))

    def pull_payment_state(self):
        """
        主动查询微信支付状态
        :return:
        """
        try:
            wx_order = WXPaymentOrder.objects.get(out_trade_no=self.order.sn)
        except WXPaymentOrder.DoesNotExist:
            raise ValueError('微信支付状态不存在')

        # 如果是未支付状态，进行更新
        if wx_order.trade_state == WXTradeStateType.NOTPAY.value:
            wx_order = wx_order_trade_state_update(self.order.sn)

        self._process_new_state(wx_order=wx_order)

    def push_payment_state(self, info):
        """
        通过回调更新微信支付状态
        :param info push回来的数据
        :return:
        """
        wx_order = parse_pay_notify(info)
        if not wx_order:
            raise ValueError('微信支付状态不存在')

        self._process_new_state(wx_order=wx_order)
