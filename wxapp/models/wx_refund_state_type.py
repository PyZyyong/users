from enum import Enum


class WXRefundStateType(Enum):
    """
    微信订单退款状态类型
    """
    SUCCESS = 1
    CHANGE = 2
    PROCESSING = 3
    REFUNDCLOSE = 4

    @classmethod
    def choices(cls):
        return (
            (WXRefundStateType.SUCCESS.value, '退款成功'),
            (WXRefundStateType.CHANGE.value, '退款异常'),
            (WXRefundStateType.PROCESSING.value, '退款处理中'),
            (WXRefundStateType.REFUNDCLOSE.value, '退款关闭'),
        )
