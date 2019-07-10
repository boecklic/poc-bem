from django.conf.urls import url, include

from rest_framework import routers, serializers, viewsets

from catalog.models import Topic, CatalogEntry
from translation.rest import TranslationKeySerializer


# Serializers define the API representation.
class TopicSerializer(serializers.ModelSerializer):
    title = TranslationKeySerializer()
    class Meta:
        model = Topic
        fields = (
            'name',
            'title',
            'staging'
        )

# ViewSets define the view behavior.
class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


# Serializers define the API representation.
# class LayersJSViewSerializer(serializers.HyperlinkedModelSerializer):
#     url = serializers.HyperlinkedIdentityField(view_name='server_layername-detail', read_only=True, lookup_field='server_layername')

#     class Meta:
#         model = LayersJSView
#         fields = (
#             'url',
#             'attribution',
#             'layertype',
#             'server_layername',
#             'topics',
#             'opacity',
#             'backgroundlayer',
#             'timestamps',
#             'bgdi_id'
#         )
class CatalogEntrySerializer(serializers.ModelSerializer):
    parent = serializers.HyperlinkedRelatedField(
        view_name='catalogentry-detail',
        read_only=True
    )
    # datasets =
    name = TranslationKeySerializer()
    class Meta:
        model = CatalogEntry
        fields = (
            'url',
            'parent',
            'datasets',
            'topic',
            'name'
        )


class CatalogEntryViewSet(viewsets.ModelViewSet):
    queryset = CatalogEntry.objects.all()
    serializer_class = CatalogEntrySerializer



# # ViewSets define the view behavior.
# class LayersJSViewViewSet(viewsets.ModelViewSet):
#     """Display some doc"""
#     queryset = LayersJSView.objects.all()
#     serializer_class = LayersJSViewSerializer
#     # lookup a single object by 'server_layername'
#     # instead of primary_key field (default)
#     lookup_field = 'server_layername'

#     # the lookup_value_regex in the url is
#     # [^/.]+ by default and hence excludes
#     # dots. to be able to use layer names such as
#     # ch.swisstopo.swisstlm3d-karte-farbe.3d,
#     # we have to change the lookup_value_regex
#     # (only exclude slash). We could also be very specific
#     # with e.g. '[a-z0-9-_.]'
#     lookup_value_regex = '[^/]+'
