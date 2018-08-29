from datetime import timedelta
from enum import Enum


class SMSCodeKey(Enum):
    """
    用户SMSCode key
    """

    # 登录
    LOGIN = 'login'
    # 申请使用
    APPLY = 'apply'

    @property
    def interval(self):
        """
        获取发送间隔
        :return:
        """
        if self is SMSCodeKey.LOGIN:
            return timedelta(seconds=60)
        if self is SMSCodeKey.APPLY:
            return timedelta(seconds=60)

        return timedelta(minutes=20)

    @property
    def valid_time(self):
        """
        获取有效期
        :return:
        """
        if self is SMSCodeKey.LOGIN:
            return timedelta(minutes=5)
        if self is SMSCodeKey.APPLY:
            return timedelta(minutes=5)
        return timedelta(minutes=20)
