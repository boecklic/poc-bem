from django.conf.urls import url, include

from rest_framework import routers, serializers, viewsets

from layers.models import Dataset
from translation.rest import TranslationKeySerializer


# Serializers define the API representation.
class DatasetSerializer(serializers.ModelSerializer):
    description = TranslationKeySerializer(read_only=True)
    short_description = TranslationKeySerializer(read_only=True)
    abstract = TranslationKeySerializer(read_only=True)
    class Meta:
        model = Dataset
        fields = (
            'url',
            'layer_name',
            'created',
            'modified',
            'description',
            'short_description',
            'abstract',
            'chargeable'
        )

# ViewSets define the view behavior.
class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
