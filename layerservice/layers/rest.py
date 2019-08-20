import json
import mappyfile

from django.conf.urls import url, include

from rest_framework import routers, serializers, viewsets, renderers
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.reverse import reverse

from rest_framework_extensions.mixins import NestedViewSetMixin

from layers.models import Dataset, MapServerLayer
from translation.rest import TranslationSerializer


# Serializers define the API representation.
class DatasetSerializer(serializers.ModelSerializer):
    description = TranslationSerializer(read_only=True)
    short_description = TranslationSerializer(read_only=True)
    abstract = TranslationSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dataset-detail',
                                               lookup_field='name')
    # mapfiles = NestedHyperlinkedRelatedField(
    #     # many=True,
    #     read_only=True,
    #     view_name='mapfiles-list',
    #     lookup_url_kwargs='dataset_pk'
    #     )
    lookup_field = 'name'
    lookup_url_kwargs = 'name'

    class Meta:
        model = Dataset
        fields = (
            'url',
            'name',
            'created',
            'modified',
            'description',
            'short_description',
            'abstract',
            'chargeable',
            # 'mapfiles'
        )

# ViewSets define the view behavior.
class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    # thy lookup should happen by the name and not by the
    # id
    lookup_field = 'name'

    # since 'name' can contain dots, we need to change the
    # default lookup_value_regex which is [^/.]+
    # https://www.django-rest-framework.org/api-guide/routers/#simplerouter
    lookup_value_regex = '[0-9a-z-_\.]+'

    # @actions
    # def mapfile(self, request, pk=None):
    #     dataset = 


class MapServerLayerHyperlink(serializers.HyperlinkedIdentityField):
    view_name = 'dataset-mapserverlayers-detail'
    # queryset = MapServerLayer.objects.all()

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'parent_lookup_group__dataset__name': obj.group.dataset.name,
            'pk': obj.id,
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            'group__dataset__name': view_kwargs['parent_lookup_group__dataset'],
            'pk': view_kwargs['pk']
        }
        return self.get_queryset().get(**lookup_kwargs)


class MapServerLayerSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source='group.name')
    # we need to declare the field here, since it's not a model field
    # but only an attribute
    name = serializers.CharField()
    type = serializers.CharField(source='group.dataset.datatype')
    url = MapServerLayerHyperlink(
        read_only=True,
        view_name='dataset-mapserverlayers-detail'
    )

    class Meta:
        model = MapServerLayer
        fields = (
            'url',
            'units',
            'template',
            'status',
            '__type__',
            'type',
            'group',
            'name',
            'metadata'
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # only include group if more than one layer exists or
        # group name is set
        if instance.group.mapserverlayer_set.count() > 1 or \
           instance.group.mapserver_group_name:
            ret['group'] = instance.group.name
        else:
            ret.pop('group', None)
        return ret


class MapfileRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'map'
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        def render_layer(layer):
            # url is not a valid field
            layer.pop('url', None)

            # wms_extent must be serialized as
            # "minx miny maxx maxy" separated by spaces instead of the
            # default json serialized form
            # "[minx, miny, maxx, maxy]"
            if 'wms_extent' in layer['metadata']:
                layer['metadata']['wms_extent'] = ' '.join(str(x) for x in layer['metadata']['wms_extent'])
            return mappyfile.dumps(layer, indent=4, spacer=' ')
        results = []
        if 'results' in data:
            res = []
            for item in data['results']:
                results.append(render_layer(item))
            mapfile = '\n\n'.join(results)
        else:
            mapfile = render_layer(data)
        return mapfile.encode(self.charset)


class MapServerLayerViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer, MapfileRenderer]
    queryset = MapServerLayer.objects.all()
    serializer_class = MapServerLayerSerializer

    # def get_queryset(self):
    #     return MapServerLayer.objects.filter(group__dataset_id=self.kwargs['dataset_pk'])