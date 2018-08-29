from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from b2c.general.helpers import retrieve_merchant_id_from_request, retrieve_wx_token_from_request
from b2c.users.models import FrontendUser


class B2CTokenAuthentication(BaseAuthentication):
    """
    微信前端验证
    """

    def authenticate(self, request):
        wx_user_token = retrieve_wx_token_from_request(request)
        merchant_id = retrieve_merchant_id_from_request(request, raise_exceptions=False)
        if not wx_user_token or not merchant_id:
            return None
        try:
            fronted_user = FrontendUser.objects.get(wx_user__token=wx_user_token)
        except FrontendUser.DoesNotExist:
            raise AuthenticationFailed()
        return fronted_user, wx_user_token
