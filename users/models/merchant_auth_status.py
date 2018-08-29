from enum import IntEnum


class MerchantAuthenticationState(IntEnum):
    """
    机构认证状态
    """
    AUTHENTICATED = 1
    UNAUTHENTICATED = 2
    UNABLE_TO_AUTHENTICATE = 3

    @classmethod
    def choices(cls):
        return (
            (MerchantAuthenticationState.AUTHENTICATED.value, '已认证'),
            (MerchantAuthenticationState.UNAUTHENTICATED.value, '未认证'),
            (MerchantAuthenticationState.UNABLE_TO_AUTHENTICATE.value, '无法认证'),
        )