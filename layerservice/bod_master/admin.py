from django.contrib import admin


from bod_master.models import Dataset, LayersJS, LayersJSView, Tileset, Topic, GeocatPublish
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

    list_display = ('id_dataset', 'get_bez_de', )
    search_fields = ('id_dataset', )
    list_filter = ('staging', 'chargeable',)
    # readonly_fields = '__all__'

    def get_bez_de(self, obj):
        return obj.geocatpublish.bezeichnung_de
    get_bez_de.short_description = 'Title DE'


@admin.register(GeocatPublish)
class GeocatPublishAdmin(EditableFieldsOnlyMixin, admin.ModelAdmin):

    list_display = ('fk_id_dataset', 'bezeichnung_de', )
    search_fields = ('fk_id_dataset', )
    # list_filter = ('staging', 'chargeable',)
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


@admin.register(Topic)
class TopicAdmin(EditableFieldsOnlyMixin, admin.ModelAdmin):

    list_display = ('topic', 'default_background', 'group_id', 'staging')
    # search_fields = ('id_dataset', )
    list_filter = ('default_background','staging')
    # readonly_fields = '__all__'