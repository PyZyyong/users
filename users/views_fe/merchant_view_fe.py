from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from b2c.general.exceptions import ServiceValidationError
from b2c.misc.serializers.media_upload_serializer import MediaUploadSerializer
from b2c.users.models import MerchantCard
from b2c.users.permissions import IsFrontendUserPermission
from b2c.users.serializers_fe.merchant_serializer_fe import MerchantCardSerializer


class MerchantCardFeView(GenericViewSet):
    permission_classes = (IsFrontendUserPermission, )

    def get_queryset(self):
        merchant_id = self.request.merchant_id
        merchant_card = MerchantCard.objects.filter(merchant_id=merchant_id).first()
        if not merchant_card:
            raise ServiceValidationError('该商户还未创建商户卡，请先创建！')
        return merchant_card

    def get_serializer_class(self):
        return MerchantCardSerializer

    @action(methods=['get'], detail=False)
    def card(self, request):
        """
        商户卡 fe-merchant-card
        :param request:
        :return:
        """

        serializer = self.get_serializer(instance=self.get_queryset())
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def card_images(self, request):
        """
        商户卡图片 fe-merchant-card-images
        :param request:
        :return:
        """
        self.pagination_class = None
        merchant_card = self.get_queryset()
        images = merchant_card.images.all()
        media_serializer = MediaUploadSerializer(
            images,
            context={'request': request},
            many=True
        )
        return Response(media_serializer.data)
