import logging
import dateutil.parser
import re
import json

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.postgres.fields import JSONField

import mappyfile

from translation.models import TranslationKey, Translation, TranslatableMixin



# import reversion
# Create your models here.
logger = logging.getLogger('default')

def validate_iso8601(value):
    try:
        parsed = dateutil.parser.parse(value)
    except Exception as e:
        raise ValidationError(e)
    return parsed

def validate_iso8601duration(value):
    # regex to validate iso 8601 duration is borrowed from
    # here: https://stackoverflow.com/a/32045167
    durex = re.compile(r"^P(?!$)(\d+(?:\.\d+)?Y)?(\d+(?:\.\d+)?M)?(\d+(?:\.\d+)?W)?(\d+(?:\.\d+)?D)?(T(?=\d)(\d+(?:\.\d+)?H)?(\d+(?:\.\d+)?M)?(\d+(?:\.\d+)?S)?)?$")
    match = durex.match(value)
    # print(value,match)
    if match:
        return value
    else:
        raise ValidationError(
            _('%(value)s is not a valid ISO 8601 duration'),
            params={'value': value}
        )

def validate_timing(value):
    if value == 'current':
        return
    
    parts = value.split(',')
    for part in parts:
        if '/' in part:
            try:
                _start,_end,_res = part.split('/')
            except ValueError as e:
                raise ValidationError(e)
            validate_iso8601(_start)
            validate_iso8601(_end)
            validate_iso8601duration(_res)
        elif part:
            validate_iso8601(part)
        else:
            # happens e.g. with trailing comma
            raise ValidationError(
                _('Empty string, maybe you have a trailing comma?')
            )


# @reversion.register()
class Dataset(TranslatableMixin, models.Model):

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    layer_name = models.CharField(max_length=512, unique=True)
    description = models.OneToOneField(
        'translation.TranslationKey',
        verbose_name=_('description'),
        on_delete=models.SET_NULL,
        related_name='dataset_description',
        null=True
    )
    short_description = models.OneToOneField(
        'translation.TranslationKey',
        verbose_name=_('short_description'),
        on_delete=models.SET_NULL,
        related_name='dataset_short_description',
        null=True
    )
    abstract = models.OneToOneField(
        'translation.TranslationKey',
        verbose_name=_('abstract'),
        on_delete=models.SET_NULL,
        related_name='dataset_abstract',
        null=True
    )

    chargeable = models.BooleanField(default=False)
    timing = models.CharField(max_length=256, help_text="""Timing can have one of 
        the following formats: 
        <pre>current | TT | TT,TT,TT | TT/TT/RES</pre>
        where <em>TT</em> is a valid ISO 8601 timestamp (e.g. 2015-05-12T13:54:01Z), 
        and <em>RES</em> is the resolution in the form <b>P</b>[n]Y[n]M[n]D<b>T</b>[n]H[n]M[n]S 
        (e.g. P1Y). Examples
        <pre>2008,2011,2012</pre>
        <pre>2005-11-01T10:15Z/2019-02-15T09:30Z/PT5M</pre>
        """, 
        default='current',
        validators=[validate_timing])

    DATATYPE_RASTER = 'raster'
    DATATYPE_POINT = 'point'
    DATATYPE_POLYGON = 'polygon'
    DATATYPE_CHOICES = (
        (DATATYPE_RASTER, 'raster'),
        (DATATYPE_POINT, 'point'),
        (DATATYPE_POLYGON, 'polygon')
    )
    datatype = models.CharField(
        max_length=32,
        choices=DATATYPE_CHOICES,
        default='polygon',
        db_index=True
    )
    

    def __str__(self):
        return self.layer_name

class Tileset(models.Model):

    # TODO LEGACY_CLEANUP: once legacy sync is dropped, add
    # auto_now_add=True and auto_now=True respectively
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    dataset = models.ForeignKey('layers.Dataset', on_delete=models.CASCADE)

    FORMAT_PNG = 'png'
    FORMAT_JPEG = 'jpeg'
    FORMAT_CHOICES = (
        (FORMAT_PNG, 'png'),
        (FORMAT_JPEG, 'jpeg')
    )
    image_type = models.CharField(max_length=10, choices=FORMAT_CHOICES, default=FORMAT_PNG)
    timestamp = models.DateTimeField(default=timezone.now)
    cache_ttl = models.PositiveIntegerField(default=1800, help_text="Cache 'time to live'")
    resolution_min = models.DecimalField(max_digits=7, decimal_places=2, default=4000.0)
    resolution_max = models.DecimalField(max_digits=7, decimal_places=2, default=0.25)
    published = models.BooleanField(default=False)
    publication_service = models.ForeignKey('publication.WMTS', null=True, blank=True, on_delete=models.SET_NULL)


class MapServerConfig(models.Model):

    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    dataset = models.ForeignKey('layers.Dataset', on_delete=models.CASCADE)

    timestamp = models.DateTimeField(default=None, null=True, blank=True)
    publication_services = models.ManyToManyField('publication.WMS')

    mapfile = models.TextField()
    mapfile_json = JSONField(blank=True)

    def __str__(self):
        return self.dataset.layer_name
    
    def clean(self):
        """clean is called during .save() to validate the model fields"""
        try:
            parsed_mapfile = mappyfile.loads(self.mapfile)
        except Exception as e:
            raise ValidationError("couldn't parse mapfile content: {}".format(e))
        else:
            self.mapfile_json = parsed_mapfile
            self.mapfile_json['metadata']['wms_title'] = self.dataset.layer_name
            self.mapfile_json['metadata']['wms_timeextent'] = self.dataset.timing