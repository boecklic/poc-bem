# from django.conf.urls import url, include

from rest_framework import routers, serializers, viewsets

from .models import BODDataset, LayersJSView


# Serializers define the API representation.
class BODDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BODDataset
        fields = ('id_dataset', 'kurzbezeichnung_de')

# ViewSets define the view behavior.
class BODDatasetViewSet(viewsets.ModelViewSet):
    queryset = BODDataset.objects.all()
    serializer_class = BODDatasetSerializer


# Serializers define the API representation.
class LayersJSViewSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='server_layername-detail', read_only=True, lookup_field='server_layername')

    class Meta:
        model = LayersJSView
        fields = (
            'url',
            'attribution',
            'layertype',
            'server_layername',
            'topics',
            'opacity',
            'backgroundlayer',
            'timestamps',
            'bgdi_id'
        )


# ViewSets define the view behavior.
class LayersJSViewViewSet(viewsets.ModelViewSet):
    """Display some doc"""
    queryset = LayersJSView.objects.all()
    serializer_class = LayersJSViewSerializer
    # lookup a single object by 'server_layername'
    # instead of primary_key field (default)
    lookup_field = 'server_layername'

    # the lookup_value_regex in the url is
    # [^/.]+ by default and hence excludes
    # dots. to be able to use layer names such as
    # ch.swisstopo.swisstlm3d-karte-farbe.3d,
    # we have to change the lookup_value_regex
    # (only exclude slash). We could also be very specific
    # with e.g. '[a-z0-9-_.]'
    lookup_value_regex = '[^/]+'
