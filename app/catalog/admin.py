from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe

from catalog.models import CatalogEntry, Topic, CatalogLayer
# from translation.models import Translation


class CatalogLayerInlineAdmin(admin.TabularInline):
    model = CatalogLayer
    extra = 1
    autocomplete_fields = ['dataset']

@admin.register(CatalogEntry)
class CatalogEntryAdmin(admin.ModelAdmin):

    list_display = ('name_de', 'parent', 'root', 'topic')
    # search_fields = ('name', )
    list_filter = ('topic', )

    inlines = [CatalogLayerInlineAdmin]
    readonly_fields = ('bodm_legacy_catalog_id', )
    # fields = ('layer_name', 'abstract_link', 'description_link')

    def root(self, obj):
        return obj.get_root()
    root.short_description = "Root Node"

    def name_de(self, obj):
        return obj.name.de if obj.name.de else obj.name.key



@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):

    list_display = ('name', 'staging')
    # search_fields = ('name', )
    list_filter = ('staging',)

    def name_de(self, obj):
        # try:
        #     return Translation.versioned.get(obj.name_key).de
        # except:
        #     return None
        return obj.name.de if obj.name.de else obj.name.key
