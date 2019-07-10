from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe

from django_ace import AceWidget
from prettyjson import PrettyJSONWidget


from layers.models import Dataset, Tileset, MapServerConfig
from translation.models import Translation


class TilesetInline(admin.StackedInline):
    model = Tileset
    readonly_fields = ('created', 'modified')
    extra = 0


class MapServerConfigForm(forms.ModelForm):

    # mapfile = forms.CharField(widget=AceWidget(
    #     mode='mapfile',
    #     width="1000px", 
    #     height="500px",
    # ))

    class Meta:
        model = MapServerConfig
        fields = ['publication_services', 'mapfile', 'mapfile_json', 'dataset']
        widgets = {
            'mapfile_json': PrettyJSONWidget(attrs={'initial': 'parsed'}),
        }


@admin.register(MapServerConfig)
class MapServerConfigAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'modified', 'publication_services_str')
    search_fields = ('dataset__layer_name',)
    form = MapServerConfigForm
    autocomplete_fields = ['dataset']
    readonly_fields = ['mapfile_json']

    def publication_services_str(self, obj):
        return ','.join(obj.publication_services.all().values_list('name', flat=True))
    publication_services_str.short_description = "Publication Services"



class MapServerConfigInline(admin.StackedInline):
    model = MapServerConfig
    form = MapServerConfigForm
    # readonly_fields = ('mapfile_json',)
    extra = 0





@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):

    list_display = ('layer_name', 'abstract' , 'timing')
    search_fields = ('layer_name', )
    list_filter = ('chargeable',)

    inlines = [TilesetInline, MapServerConfigInline]
    readonly_fields = ('abstract_link', 'description_link')
    fields = ('layer_name', 'abstract_link', 'description_link', 'timing')



    def abstract_link(self, obj):
        url = reverse("admin:translation_translationkey_change", args=(obj.abstract_id,))
        return mark_safe("<a target=_blank href='{}'>{}</a>".format(url, obj.abstract_id))
    abstract_link.allow_tags = True
    abstract_link.short_description = "Abstract"

    def description_link(self, obj):
        url = reverse("admin:translation_translationkey_change", args=(obj.description_id,))
        return mark_safe("<a target=_blank href='{}'>{}</a>".format(url, obj.description_id))
    description_link.allow_tags = True
    description_link.short_description = "Description"


