from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe

from provider.models import Provider, Attribution
from translation.models import Translation

# Register your models here.

class AttributionInline(admin.TabularInline):
    model = Attribution
    extra = 0
    # autocomplete_fields = ('name', )
    fields = ('prefix','name')



@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):

    list_display = ('name',)
    inlines = [AttributionInline]

    # def name_de(self, obj):
    #     try:
    #         return Translation.versioned.get(pk=obj.name_id).de
    #     except:
    #         return None



@admin.register(Attribution)
class AttributionAdmin(admin.ModelAdmin):

    list_display = ('name_de', 'short_de', 'provider')
    list_filter = ('provider', )
    search_fields = ('provider', )
    readonly_fields = ('name_link', 'short_link')

    fields = (
        'provider',
        'name_link',
        'short_link'
    )

    def name_de(self, obj):
        try:
            return Translation.versioned.get(pk=obj.name_id).de
        except:
            return None


    def short_de(self, obj):
        try:
            return Translation.versioned.get(pk=obj.short_id).de
        except:
            return None

    def name_link(self, obj):
        url = reverse("admin:translation_translation_change", args=(obj.name_id,))
        print(url)
        return mark_safe("{}&nbsp;(edit: <a target=_blank href='{}'>{}</a>)".format(
            obj.name.full_translation_list(),
            url,
            obj.name_id
        ))
    name_link.allow_tags = True
    name_link.short_description = "Name"


    def short_link(self, obj):
        url = reverse("admin:translation_translation_change", args=(obj.short_id,))
        print(url)
        return mark_safe("{}&nbsp;(edit: <a target=_blank href='{}'>{}</a>)".format(
            obj.short.full_translation_list(),
            url,
            obj.short_id
        ))
    short_link.allow_tags = True
    short_link.short_description = "Short"

