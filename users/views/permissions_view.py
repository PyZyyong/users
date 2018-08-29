from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from b2c.general.mixins import SimpleCodenamePermissionMixin
from b2c.users.schema import permission_schema


class PermissionsView(GenericViewSet,
                      mixins.ListModelMixin,
                      SimpleCodenamePermissionMixin):
    filter_class = []
    permission_codenames = ['users.mb_merchant_user_set_group']

    def list(self, request):
        """
        权限列表获取 mb-permissions
        :param request:
        :return:
        """
        return Response(permission_schema)
