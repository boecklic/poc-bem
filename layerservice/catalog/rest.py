from django.conf.urls import url, include

from rest_framework import routers, serializers, viewsets
from rest_framework.reverse import reverse
from rest_framework_extensions.mixins import NestedViewSetMixin

from catalog.models import Topic, CatalogEntry
# from layers.rest import DatasetSerializer
from translation.rest import TranslationSerializer



# Serializers define the API representation.
class TopicSerializer(serializers.ModelSerializer):
    title_key = TranslationSerializer()
    class Meta:
        model = Topic
        fields = (
            'name',
            'title_key',
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

class TopicEntriesHyperlink(serializers.HyperlinkedIdentityField):
    view_name = 'topic-entries-detail'
    # queryset = MapServerLayer.objects.all()

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'parent_lookup_topic_id': obj.topic_id,
            'pk': obj.id,
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            'topic_id': view_kwargs['parent_lookup_topic_id'],
            'pk': view_kwargs['pk']
        }
        return self.get_queryset().get(**lookup_kwargs)


class CatalogEntrySerializer(serializers.ModelSerializer):
    # Create full url instead of bare raw id of related object
    url = TopicEntriesHyperlink(
        view_name='topic-entries-detail',
        read_only=True
    )
    # parent = TopicEntriesHyperlink(
    #     view_name='topic-entries-detail',
    #     read_only=True
    # )
    datasets = serializers.HyperlinkedRelatedField(
        view_name='dataset-detail',
        lookup_field='name',
        many=True,
        read_only=True
    )
    topic = serializers.HyperlinkedRelatedField(
        view_name='topic-detail',
        read_only=True
    )
    name = TranslationSerializer()
    class Meta:
        model = CatalogEntry
        fields = (
            'url',
            'parent',
            'datasets',
            'topic',
            'name'
        )


class CatalogEntryViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
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
