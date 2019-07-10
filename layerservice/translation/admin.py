from django.contrib import admin

# Register your models here.

from translation.models import Translation, TranslationKey


class TranslationInline(admin.StackedInline):
    model = Translation
    fields = ['de','fr', 'it', 'en', 'rm']
    # readonly_fields = ['de', 'fr']
    extra = 0
    max_num = 1
    can_delete = False
    readonly_fields = ['revision', 'current', 'translation_key']
    verbose_name = "Current Translation"


    def get_queryset(self, request):
        return super().get_queryset(request).filter(current=True)    


class OldTranslationInline(admin.TabularInline):
    model = Translation
    fields = ['de','fr', 'it', 'en', 'rm']
    extra = 0
    max_num = 1
    can_delete = False
    readonly_fields = ['revision', 'current', 'translation_key', 'de','fr', 'it', 'en', 'rm']
    verbose_name = "Old Translation"
    verbose_name_plural = "Old Translations"

    def get_queryset(self, request):
        return super().get_queryset(request).filter(current=False).order_by('-created')

@admin.register(TranslationKey)
class TranslationKeyAdmin(admin.ModelAdmin):

    list_display = ('id', )
    search_fields = ('id', 'translation__de', 'translation__fr', 'translation__it', 'translation__en', 'translation__rm')
    # list_filter = ('staging', 'chargeable',)
    readonly_fields = ['id']
    fields = ('id',)
    inlines = [TranslationInline, OldTranslationInline]


# @admin.register(Translation)
# class TranslationAdmin(admin.ModelAdmin):

#     list_display = ('translation_key', 'de', 'fr')
#     search_fields = ('de', 'fr', 'en', 'it', 'rm')
#     readonly_fields = ('revision', 'current', 'created')
