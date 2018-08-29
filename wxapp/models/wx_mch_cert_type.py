from enum import Enum


class WXMchCertType(Enum):
    """
    证书类型
    """
    CERT_PEM = 1
    KEY_PEM = 2

    @classmethod
    def choices(cls):
        return (
            (WXMchCertType.CERT_PEM.value, '证书'),
            (WXMchCertType.KEY_PEM.value, '证书密钥')
        )
