from django.contrib import admin
from django.db.models import Count


from bod_master.models import BODDataset, LayersJS, LayersJSView, Tileset, Topic, GeocatPublish, GeocatImport
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


class BODDatasetGeocatIDDuplicateFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "duplicates"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "duplicates"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [
            ("duplicate", "duplicate Geocat ID"),
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'duplicate':
            dupes = queryset.values('fk_geocat').annotate(Count('id')).values('fk_geocat').order_by().filter(id__count__gt=1)
            recs = queryset.filter(fk_geocat__in=dupes)
            return recs
        else:
            return queryset



@admin.register(BODDataset)
class BODDatasetAdmin(EditableFieldsOnlyMixin, admin.ModelAdmin):

    list_display = ('id_dataset', 'get_bez_de', 'fk_geocat' )
    search_fields = ('id_dataset', )
    list_filter = ('staging', 'chargeable', BODDatasetGeocatIDDuplicateFilter)
    # readonly_fields = '__all__'

    def get_bez_de(self, obj):
        return obj.geocatpublish.bezeichnung_de
    get_bez_de.short_description = 'Title DE'


@admin.register(GeocatImport)
class GeocatImportAdmin(EditableFieldsOnlyMixin, admin.ModelAdmin):

    list_display = ('id', 'geocat_bezeichnung_de', )
    # search_fields = ('fk_id_dataset', )
    # list_filter = ('staging', 'chargeable',)
    # readonly_fields = '__all__'


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
