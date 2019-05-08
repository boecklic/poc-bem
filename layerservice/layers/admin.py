from django.contrib import admin


from .models import Dataset, LayersJS, LayersJSView, Tileset
# Register your models here.

class EditableFieldsOnlyMixin(object):
    def get_readonly_fields(self, request, obj=None):
        editable_fields = getattr(self, 'editable_fields', [])

        return [f.name for f in self.model._meta.fields if not f.name in editable_fields]


@admin.register(Tileset)
class TilesetAdmin(admin.ModelAdmin):

    list_display = ('fk_dataset_id', 'published', 'timestamp', 'bgdi_modified')
    list_filter = ('published', 'timestamp',)
    search_fields = ('fk_dataset_id',)


@admin.register(Dataset)
class DatasetAdmin(EditableFieldsOnlyMixin, admin.ModelAdmin):

    list_display = ('id_dataset', 'frm_bezeichnung_de', )
    search_fields = ('id_dataset', )
    list_filter = ('staging', 'chargeable',)
    # readonly_fields = '__all__'


@admin.register(LayersJS)
class LayersJSAdmin(EditableFieldsOnlyMixin, admin.ModelAdmin):

    list_display = ('pk_layer', 'layertype', 'image_format')
    # search_fields = ('id_dataset', )
    list_filter = ('layertype','image_format')
    # readonly_fields = '__all__'
    editable_fields = ('layertype', )


@admin.register(LayersJSView)
class LayersJSViewAdmin(EditableFieldsOnlyMixin, admin.ModelAdmin):

    list_display = ('layer_id', 'layertype', 'image_format')
    # search_fields = ('id_dataset', )
    list_filter = ('layertype','image_format')
    # readonly_fields = '__all__'