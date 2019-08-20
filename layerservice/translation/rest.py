from django.conf.urls import url, include

from rest_framework import routers, serializers, viewsets

from translation.models import Translation


# Serializers define the API representation.
class TranslationSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedRelatedField(
    #     view_name='translation-detail',
    #     read_only=True
    # )
    class Meta:
        model = Translation
        read_only_fields = ('key',)
        fields = (
            'url',
            'key',
            'de',
            'fr',
            'en',
            'it',
            'rm'
        )

# ViewSets define the view behavior.
class TranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.versioned.all()
    serializer_class = TranslationSerializer


# class TranslationKeySerializer(serializers.ModelSerializer):
#     translation = TranslationSerializer()
#     class Meta:
#         model = TranslationKey
#         fields = (
#             'id',
#             'translation'
#         )

# class TranslationKeyViewSet(viewsets.ModelViewSet):
#     queryset = TranslationKey.objects.all()
#     serializer_class = TranslationKeySerializer
