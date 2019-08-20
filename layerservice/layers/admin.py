from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe

from django_ace import AceWidget
from prettyjson import PrettyJSONWidget


from layers.models import Dataset, Tileset, MapServerGroup, MapServerLayer
from translation.models import Translation


class TilesetInline(admin.StackedInline):
    model = Tileset
    readonly_fields = ('created', 'modified')
    extra = 0


class MapServerLayerForm(forms.ModelForm):

    # mapfile = forms.CharField(widget=AceWidget(
    #     mode='mapfile',
    #     width="1000px", 
    #     height="500px",
    # ))

    class Meta:
        model = MapServerLayer
        fields = [
            'mapserver_layer_name',
            'wms_extent',
            'wms_enable_request',
            'units',
            'status',
            'mapfile',
            'mapfile_json',
        ]
        widgets = {
            'mapfile_json': PrettyJSONWidget(attrs={'initial': 'parsed'}),
        }


@admin.register(MapServerLayer)
class MapServerLayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_name', 'dataset_name', 'modified')
    search_fields = ('group__dataset__name',)
    form = MapServerLayerForm
    # autocomplete_fields = ['dataset']
    readonly_fields = ['mapfile']

    def dataset_name(self, obj):
        return obj.group.dataset.name

    def group_name(self, obj):
        return obj.group.mapserver_group_name or None


class MapServerLayerInline(admin.StackedInline):
    model = MapServerLayer
    form = MapServerLayerForm
    # readonly_fields = ('mapfile_json',)
    extra = 1


@admin.register(MapServerGroup)
class MapServerGroupAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'publication_services_str')
    search_fields = ('dataset__name',)
    autocomplete_fields = ['dataset']
    inlines = [MapServerLayerInline]

    def publication_services_str(self, obj):
        return ','.join(obj.publication_services.all().values_list('name', flat=True))
    publication_services_str.short_description = "Publication Services"


def get_translation_pk_for_key(key):
    try:
        return Translation.versioned.get(key=key).pk
    except Exception as e:
        return None


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):

    list_display = ('name', 'abstract_de' , 'timing')
    search_fields = ('name', )
    list_filter = ('chargeable', 'srs')

    inlines = [TilesetInline]
    readonly_fields = ('abstract_link', 'description_link')
    fields = (
        'name',
        'abstract_link',
        'description_link',
        'timing',
        'datatype',
        'srs'
    )

    def abstract_de(self, obj):
        try:
            return Translation.versioned.get(key=obj.abstract_key).de
        except:
            return None

    def abstract_link(self, obj):
        _id = get_translation_pk_for_key(obj.abstract_key)
        url = reverse("admin:translation_translation_change", args=(_id,))
        return mark_safe("{}&nbsp;(edit: <a target=_blank href='{}'>{}</a>)".format(
            self.abstract_de(obj),
            url,
            obj.abstract_key
        ))
    abstract_link.allow_tags = True
    abstract_link.short_description = "Abstract"

    def description_de(self, obj):
        try:
            return Translation.versioned.get(key=obj.description_key).de
        except:
            return None

    def description_link(self, obj):
        _id = get_translation_pk_for_key(obj.description_key)
        url = reverse("admin:translation_translation_change", args=(_id,))
        return mark_safe("{}&nbsp;(edit: <a target=_blank href='{}'>{}</a>)".format(
            self.description_de(obj),
            url,
            obj.description_key
        ))
    description_link.allow_tags = True
    description_link.short_description = "Description"


