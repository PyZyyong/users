from django.http.response import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import ValidationError

from b2c.general.helpers import retrieve_merchant_id_from_request


class MerchantMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        not_ignore_path = ('fe', 'mb')
        request_path = request.path.split('/')
        if not request_path[2] in not_ignore_path:
            return None
        try:
            merchant_id = retrieve_merchant_id_from_request(request)
        except ValidationError:
            return HttpResponseForbidden("获取不到商户id 请求头缺少 X-MERCHANT-ID")
        if not merchant_id:
            return HttpResponseForbidden("获取不到商户id 请求头缺少 X-MERCHANT-ID")

        setattr(request, "merchant_id", merchant_id)
        return None
