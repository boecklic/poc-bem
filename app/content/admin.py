from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe


from content.models import WMS




@admin.register(WMS)
class WMSAdmin(admin.ModelAdmin):

    list_display = ('name', 'staging' , 'fqdn')
    search_fields = ('name', )
    list_filter = ('staging',)

    # inlines = [TilesetInline]
    # readonly_fields = ('abstract_link', 'description_link')
    # fields = ('layer_name', 'abstract_link', 'description_link', 'timing')
