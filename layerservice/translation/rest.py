from django.conf.urls import url, include

from rest_framework import routers, serializers, viewsets

from translation.models import Translation, TranslationKey


# Serializers define the API representation.
class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = (
            'de',
            'fr',
            'en',
            'it',
            'rm'
        )

# ViewSets define the view behavior.
# class TranslationViewSet(viewsets.ModelViewSet):
#     queryset = Translation.objects.all()
#     serializer_class = TranslationSerializer


class TranslationKeySerializer(serializers.ModelSerializer):
    translation = TranslationSerializer()
    class Meta:
        model = TranslationKey
        fields = (
            'id',
            'translation'
        )

class TranslationKeyViewSet(viewsets.ModelViewSet):
    queryset = TranslationKey.objects.all()
    serializer_class = TranslationKeySerializer
