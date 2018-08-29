from enum import Enum


class WXTradeStateType(Enum):
    """
    微信订单交易状态类型
    """
    SUCCESS = 1
    REFUND = 2
    NOTPAY = 3
    CLOSED = 4
    REVOKED = 5
    USERPAYING = 6
    PAYERROR = 7

    @classmethod
    def choices(cls):
        return (
            (WXTradeStateType.SUCCESS.value, '支付成功'),
            (WXTradeStateType.REFUND.value, '转入退款'),
            (WXTradeStateType.NOTPAY.value, '未支付'),
            (WXTradeStateType.CLOSED.value, '已关闭'),
            (WXTradeStateType.REVOKED.value, '已撤销（刷卡支付）'),
            (WXTradeStateType.USERPAYING.value, '用户支付中'),
            (WXTradeStateType.PAYERROR.value, '支付失败(其他原因，如银行返回失败)')
        )
