import json
from typing import Any
from django import forms
from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from django.forms.widgets import Textarea
from django.urls import reverse
from django.utils.html import mark_safe
from django.db.models import Count
from django.contrib.admin import SimpleListFilter
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from django_ace import AceWidget
from prettyjson import PrettyJSONWidget


from admin_auto_filters.filters import AutocompleteFilter

from distribution.models import Dataset, FeatureCollection, RasterCollection, DownloadCollection, VectorModel#, Tileset, MapServerGroup, MapServerLayer
from translation.models import Translation
from translation.admin import TranslationInline



def get_translation_pk_for_key(key):
    try:
        return Translation.versioned.get(key=key).pk
    except Exception as e:
        return None



class FeatureCollectionInline(admin.TabularInline):
    model = FeatureCollection
    extra = 0


class RasterCollectionInline(admin.TabularInline):
    model = RasterCollection
    extra = 0


class DownloadCollectionInline(admin.TabularInline):
    model = DownloadCollection
    extra = 0



# Filter to have 'current=true' selected by default
class NrFeatureCollectionsFilter(SimpleListFilter):
    title = _('# Feature Collections')

    parameter_name = 'nr_featcol'

    def lookups(self, request, model_admin):
        return (
            ('0', _('0')),
            ('1', _('1')),
            ('several', _('> 1')),
        )

    def queryset(self, request, queryset):
        queryset = queryset.select_related().annotate(featurecollection_count=Count('featurecollection'))
        if self.value() == '0':
            return queryset.filter(featurecollection_count=0)
        elif self.value() == '1':
            return queryset.filter(featurecollection_count=1)
        elif self.value() == 'several':
            return queryset.filter(featurecollection_count__gt=1)


class NrRasterCollectionsFilter(SimpleListFilter):
    title = _('# Raster Collections')

    parameter_name = 'nr_rastcol'

    def lookups(self, request, model_admin):
        return (
            ('0', _('0')),
            ('1', _('1')),
            ('several', _('> 1')),
        )

    def queryset(self, request, queryset):
        queryset = queryset.select_related().annotate(rastercollection_count=Count('rastercollection'))
        if self.value() == '0':
            return queryset.filter(rastercollection_count=0)
        elif self.value() == '1':
            return queryset.filter(rastercollection_count=1)
        elif self.value() == 'several':
            return queryset.filter(rastercollection_count__gt=1)


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):

    list_display = ('name', 'abstract_de', 'provider', 'geocat_id', 'nr_featcol', 'nr_rastercol', 'nr_downloadcol')#, 'abstract_link')#, 'timing')
    search_fields = ('name', 'geocat_id')
    list_filter = ('provider', NrFeatureCollectionsFilter, NrRasterCollectionsFilter)

    inlines = [FeatureCollectionInline, RasterCollectionInline, DownloadCollectionInline]
    readonly_fields = ('abstract_link', 'description_link', 'geocat_id')
    # form = DatasetModelForm
    fields = (
        'name',
    #     'abstract',
        'abstract_link',
        'description_link',
        'provider',
        'attribution',
        'geocat_id'
    # #     # 'timing',
    # #     # 'datatype',
    # #     # 'srs'
    )

    def abstract_de(self, obj):
        try:
            return Translation.versioned.get(pk=obj.abstract_id).de
        except:
            return None

    def abstract_link(self, obj):
        url = reverse("admin:translation_translation_change", args=(obj.abstract_id,))
        print(url)
        return mark_safe("{}&nbsp;(edit: <a target=_blank href='{}'>{}</a>)".format(
            obj.abstract.full_translation_list(),
            url,
            obj.abstract_id
        ))
    abstract_link.allow_tags = True
    abstract_link.short_description = "Abstract"

    def nr_featcol(self, obj):
        return obj.featurecollection_set.count()
    nr_featcol.short_description = "# FeatColl"

    def nr_rastercol(self, obj):
        return obj.rastercollection_set.count()
    nr_rastercol.short_description = "# RastColl"

    def nr_downloadcol(self, obj):
        return obj.downloadcollection_set.count()
    nr_downloadcol.short_description = "# DownloadCol"

    def description_de(self, obj):
        try:
            return Translation.versioned.get(pk=obj.description_id).de
        except:
            return None

    def description_link(self, obj):
        url = reverse("admin:translation_translation_change", args=(obj.description_id,))
        return mark_safe("{}&nbsp;(edit: <a target=_blank href='{}'>{}</a>)".format(
            obj.description.full_translation_list(),
            url,
            obj.description_id
        ))
    description_link.allow_tags = True
    description_link.short_description = "Description"


class DatasetFilter(AutocompleteFilter):
    title = 'Dataset'  # display title
    field_name = 'dataset'  # name of the foreign key



@admin.register(FeatureCollection)
class FeatureCollectionAdmin(admin.ModelAdmin):
    list_display = ('slug', 'db_name', 'db_schema', 'db_table', 'used_in_feature_api', 'used_in_wms_layer')
    search_fields = ('slug', )
    list_filter = ('used_in_feature_api', 'used_in_wms_layer', DatasetFilter)
    autocomplete_fields = ('dataset', )

    formfield_overrides = {
        ArrayField: {'widget': Textarea}
    }

@admin.register(RasterCollection)
class RasterCollectionAdmin(admin.ModelAdmin):
    list_display = ('slug', 'file', 'tiled')
    search_fields = ('slug', )
    list_filter = ('tiled', )
    autocomplete_fields = ('dataset', )

    # formfield_overrides = {
    #     ArrayField: {'widget': Textarea}
    # }

@admin.register(DownloadCollection)
class DownloadCollectionAdmin(admin.ModelAdmin):
    list_display = ('slug', 'in_stac')
    search_fields = ('slug', )
    list_filter = ('in_stac', )
    autocomplete_fields = ('dataset', )

    # formfield_overrides = {
    #     ArrayField: {'widget': Textarea}
    # }


class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=2, sort_keys=True, **kwargs)



@admin.register(VectorModel)
class VectorModelAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    list_filter = ('provider', )
    # readonly_fields = ('db_fields', 'chsdi_fields')

    def get_form(self, *args, **kwargs: Any) -> Any:
        form = super().get_form(*args, **kwargs)
        print(form.base_fields)
        form.base_fields['db_fields'].encoder = PrettyJSONEncoder
        form.base_fields['chsdi_fields'].encoder = PrettyJSONEncoder
        return form
