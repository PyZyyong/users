from enum import Enum


class WXAppReviewStateType(Enum):
    """
    小程序审核状态类型
    """
    SUCCESS = 1
    FAILED = 2
    PROCESSING = 3

    @classmethod
    def choices(cls):
        return (
            (WXAppReviewStateType.SUCCESS.value, '审核成功'),
            (WXAppReviewStateType.FAILED.value, '审核失败'),
            (WXAppReviewStateType.PROCESSING.value, '审核中'),
        )
