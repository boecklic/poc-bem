import json
import mappyfile
from collections import OrderedDict


from rest_framework import routers, serializers, viewsets, renderers
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.reverse import reverse
from rest_framework.relations import PKOnlyObject

from rest_framework_extensions.mixins import NestedViewSetMixin

from provider.models import Provider, Attribution


class RemoveNullKeysSearializerMixin():
    # stolen from https://stackoverflow.com/a/27016674

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # KEY IS HERE:
            if attribute in [None, '']:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret



# Serializers define the API representation.
class ProviderSerializer(RemoveNullKeysSearializerMixin, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='provider-detail')
                                            #    lookup_field='name')
    # lookup_field = 'name'
    # lookup_url_kwargs = 'name'

    class Meta:
        model = Provider
        fields = (
            'url',
            'name',
            'prefix'
        )

# ViewSets define the view behavior.
class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

    # thy lookup should happen by the name and not by the
    # id
    # lookup_field = 'name'

    # since 'name' can contain dots, we need to change the
    # default lookup_value_regex which is [^/.]+
    # https://www.django-rest-framework.org/api-guide/routers/#simplerouter
    lookup_value_regex = '[0-9a-z-_\.]+'

