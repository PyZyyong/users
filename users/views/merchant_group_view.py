from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from b2c.general.mixins import SimpleCodenamePermissionMixin
from b2c.users.models import MerchantGroup, Merchant
from b2c.users.serializers import merchant_group_serializer


class MerchantGroupView(ModelViewSet, SimpleCodenamePermissionMixin):
    """
    list: 商户用户组列表	mb-groups
    create: 商户用户组创建	mb-create-group
    update: 商户用户组修改	mb-update-group
    retrieve: 商户用户组详情	mb-group-detail
    destroy: 商户组删除	mb-delete-group
    """
    filter_class = []
    permission_codenames = ['users.mb_merchant_user_set_group']
    permission_classes = [TokenHasReadWriteScope]

    def get_queryset(self):
        merchant = Merchant.objects.get(id=self.request.merchant_id)
        queryset = MerchantGroup.objects.filter(merchant=merchant) \
            .order_by('-created_at')
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return merchant_group_serializer.MerchantGroupListSerializer
        if self.action == 'retrieve':
            return merchant_group_serializer.MerchantGroupRetrieveSerializer
        if self.action == 'group_list':
            return merchant_group_serializer.GroupListSerializer
        return merchant_group_serializer.MerchantGroupSerializer

    def destroy(self, request, pk):
        merchant_group = MerchantGroup.objects.get(id=pk)
        serializer = merchant_group_serializer.MerchantGroupDelSerializer(instance=merchant_group,
                                                data=request.data)
        if serializer.is_valid():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'msg': '组中存在用户, 无法删除!'}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def group_list(self, request):
        """
        组列表 不分页
        :param request:
        :return:
        """
        self.permission_classes = []
        self.pagination_class = None
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(serializer.data)