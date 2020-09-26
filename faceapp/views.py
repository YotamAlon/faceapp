from faceapp.models import Image, FaceRequest
from rest_framework import routers, serializers, viewsets, mixins
from threading import Thread


class FaceRequestSerializer(serializers.HyperlinkedModelSerializer):
    image_urls = serializers.ListField(child=serializers.CharField(), allow_empty=False)

    class Meta:
        model = FaceRequest
        fields = ['id', 'url', 'status', 'error', 'best_image', 'image_urls']
        read_only_fields = ['id', 'url', 'status', 'error', 'best_image']

    def create(self, validated_data):
        image_urls = validated_data.pop('image_urls')

        face_request = super().create(validated_data)

        for image_url in image_urls:
            image = Image(url=image_url, request=face_request)
            image.save()

        Thread(target=face_request.execute).start()

        return face_request


# We list the exact mixins we want to use. In this case we do not allow updates
class FaceRequestViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                         mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = FaceRequest.objects.all()
    serializer_class = FaceRequestSerializer


router = routers.DefaultRouter()
router.register(r'', FaceRequestViewSet)
