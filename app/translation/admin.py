from typing import Any
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from django.utils.translation import gettext_lazy as _


# Register your models here.

from translation.models import Translation


class TranslationInline(admin.StackedInline):
    model = Translation
    fields = ['de','fr', 'it', 'en', 'rm']
    # readonly_fields = ['de', 'fr']
    extra = 0
    max_num = 1
    can_delete = False
    readonly_fields = ['revision', 'current', 'key']
    verbose_name = "Current Translation"


    def get_queryset(self, request):
        return super().get_queryset(request).filter(current=True)


class OldTranslationInline(admin.TabularInline):
    model = Translation
    fields = ['de','fr', 'it', 'en', 'rm']
    extra = 0
    max_num = 1
    can_delete = False
    readonly_fields = ['revision', 'current', 'key', 'de','fr', 'it', 'en', 'rm']
    verbose_name = "Old Translation"
    verbose_name_plural = "Old Translations"

    def get_queryset(self, request):
        return super().get_queryset(request).filter(current=False).order_by('-created')



# Filter to have 'current=true' selected by default
class CurrentFilter(SimpleListFilter):
    title = _('Current')

    parameter_name = 'current'

    def lookups(self, request, model_admin):
        return (
            (None, _('Yes')),
            ('no', _('No')),
            ('all', _('All')),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(current=False)
        elif self.value() is None:
            return queryset.filter(current=True)



def revert(modeladmin, request, queryset):
    for obj in queryset.all():
        if obj.revision < 1:
            # nothing to revert
            continue
        obj.__class__.objects.filter(key=obj.key, revision=obj.revision-1).update(current=True)
        obj.delete()

revert.short_description = "Revert to previous revision"



@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):

    list_display = ('key', 'revision', 'de', 'fr')
    search_fields = ('key', 'de', 'fr', 'it', 'en', 'rm')
    list_filter = ((CurrentFilter),)
    # list_filter = (('current'),)
    readonly_fields = ['key','revision']
    fields = ('key','revision', 'de','fr','it','en','rm')
    # inlines = [OldTranslationInline]
    actions = [revert]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        # use our manager, rather than the default one
        return self.model.objects.get_queryset()

# @admin.register(Translation)
# class TranslationAdmin(admin.ModelAdmin):

#     list_display = ('translation_key', 'de', 'fr')
#     search_fields = ('de', 'fr', 'en', 'it', 'rm')
#     readonly_fields = ('revision', 'current', 'created')
