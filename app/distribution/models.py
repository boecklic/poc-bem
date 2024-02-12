import logging
import dateutil.parser
import re
import json
import mappyfile

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from django.contrib.postgres.fields import ArrayField


# from compositefk.fields import CompositeOneToOneField

# from translation.models import Translation



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



class Dataset(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=512, unique=True, db_index=True)
    geocat_id = models.CharField(max_length=128, blank=True, null=True, unique=True)
    provider = models.ForeignKey('provider.Provider', null=True, blank=True, on_delete=models.SET_NULL)
    attribution = models.ForeignKey('provider.Attribution', on_delete=models.SET_NULL, null=True)

    description = models.ForeignKey(
        'translation.Translation',
        verbose_name=_('description'),
        on_delete=models.SET_NULL,
        related_name='dataset_description',
        null=True
    )

    short_description = models.OneToOneField(
        'translation.Translation',
        verbose_name=_('short_description'),
        on_delete=models.SET_NULL,
        related_name='dataset_short_description',
        null=True
    )

    abstract = models.OneToOneField(
        'translation.Translation',
        verbose_name=_('abstract'),
        on_delete=models.SET_NULL,
        related_name='dataset_abstract',
        null=True
    )

    # chargeable = models.BooleanField(default=False)
    # timing = models.CharField(max_length=256, help_text="""Timing can have one of
    #     the following formats:
    #     <pre>current | TT | TT,TT,TT | TT/TT/RES</pre>
    #     where <em>TT</em> is a valid ISO 8601 timestamp (e.g. 2015-05-12T13:54:01Z),
    #     and <em>RES</em> is the resolution in the form <b>P</b>[n]Y[n]M[n]D<b>T</b>[n]H[n]M[n]S
    #     (e.g. P1Y). Examples
    #     <pre>2008,2011,2012</pre>
    #     <pre>2005-11-01T10:15Z/2019-02-15T09:30Z/PT5M</pre>
    #     """,
    #     default='current',
    #     validators=[validate_timing])

    # DATATYPE_RASTER = 'raster'
    # DATATYPE_POINT = 'point'
    # DATATYPE_POLYGON = 'polygon'
    # DATATYPE_CHOICES = (
    #     (DATATYPE_RASTER, 'raster'),
    #     (DATATYPE_POINT, 'point'),
    #     (DATATYPE_POLYGON, 'polygon')
    # )
    # datatype = models.CharField(
    #     max_length=32,
    #     choices=DATATYPE_CHOICES,
    #     default='polygon',
    #     db_index=True
    # )

    # srs = models.ForeignKey(
    #     'geo.SRS',
    #     on_delete=models.SET_NULL,
    #     null=True
    # )

    # Todo: Make this FK to db model which is synced with
    # actual DB
    db_name = models.CharField(max_length=64, null=True)

    def __str__(self):
        return self.name


class Distribution(models.Model):
    dataset = models.ForeignKey('distribution.Dataset', on_delete=models.CASCADE)
    title = models.CharField(max_length=256, null=True, blank=True)
    slug = models.SlugField(max_length=128, default='all')

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.slug


#     WMS = 'wms'
#     WMTS = 'wmts'
#     FEATURE = 'feature'
#     EDR = 'edr'
#     DOWNLOAD = 'download'
#     TYP_CHOICES = (
#         (WMS, 'WMS'),
#         (WMTS, 'WMTS')
#     )
#     typ = models.CharField(max_length=32, choices=TYP_CHOICES)

class FeatureCollection(Distribution):

    mf_chsdi_file = models.CharField(max_length=256, null=True, blank=True)
    mf_chsdi_models = ArrayField(models.CharField(max_length=64), blank=True, null=True)
    mf_chsdi_model_definitions = ArrayField(models.TextField(), blank=True, null=True)
    used_in_feature_api = models.BooleanField(default=False)
    used_in_wms_layer = models.BooleanField(default=False)
    mapfile_data_string = models.CharField(max_length=2048, null=True, blank=True)
    db_name = models.CharField(max_length=256, null=True, blank=True)
    db_schema = models.CharField(max_length=64, null=True, blank=True)
    db_table = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        unique_together = ('dataset', 'slug')


class DownloadCollection(Distribution):

    in_stac = models.BooleanField(default=False)

    class Meta:
        unique_together = ('dataset', 'slug')


class RasterCollection(Distribution):

    file = models.CharField(max_length=512, null=True, blank=True)
    tiled = models.BooleanField(default=False)

    class Meta:
        unique_together = ('dataset', 'slug')
        unique_together = ('slug', 'file')


class VectorModel(models.Model):
    provider = models.ForeignKey('provider.Provider', on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    db_fields = models.JSONField(null=True)
    chsdi_fields = models.JSONField(null=True)


class VectorField(models.Model):
    TYPE_TEXT = 'text'
    TYPE_DOUBLE = 'double precision'
    TYPE_TIMESTAMP_NTZ = 'timestamp without time zone'
    TYPE_INTEGER = 'integer'
    TYPE_CHAR = 'character varying'
    TYPE_GEOMETRY = 'geometry'
    TYPE_UNKNOWN = 'unknown'

    TYPE_CHOICES = (
        (TYPE_TEXT, 'text'),
        (TYPE_DOUBLE, 'double precision'),
        (TYPE_TIMESTAMP_NTZ, 'timestamp without time zone'),
        (TYPE_INTEGER, 'integer'),
        (TYPE_CHAR, 'character varying'),
        (TYPE_GEOMETRY, 'geometry'),
        (TYPE_UNKNOWN, 'unknown')
    )
    vectormodel = models.ForeignKey('distribution.VectorModel', on_delete=models.CASCADE)
    typ = models.CharField(choices=TYPE_CHOICES, max_length=128)
    public = models.BooleanField(default=True)


class VectorStyle(models.Model):
    vectormodel = models.ForeignKey('distribution.VectorModel', on_delete=models.CASCADE)
    style = models.TextField()


# class Metadata(models.Model):

#     dataset = models.OneToOneField('layers.Dataset', on_delete=models.CASCADE)
#     url_infos = models.URLField(max_length=1024, null=True, blank=True)
#     url_download = models.URLField(max_length=1024, null=True, blank=True)
#     url_portal = models.URLField(max_length=1024, null=True, blank=True)


# class Tileset(models.Model):

#     # TODO LEGACY_CLEANUP: once legacy sync is dropped, add
#     # auto_now_add=True and auto_now=True respectively
#     created = models.DateTimeField(default=timezone.now)
#     modified = models.DateTimeField(default=timezone.now)
#     dataset = models.ForeignKey('layers.Dataset', on_delete=models.CASCADE)

#     FORMAT_PNG = 'png'
#     FORMAT_JPEG = 'jpeg'
#     FORMAT_CHOICES = (
#         (FORMAT_PNG, 'png'),
#         (FORMAT_JPEG, 'jpeg')
#     )
#     image_type = models.CharField(max_length=10, choices=FORMAT_CHOICES, default=FORMAT_PNG)
#     timestamp = models.DateTimeField(default=timezone.now)
#     cache_ttl = models.PositiveIntegerField(default=1800, help_text="Cache 'time to live'")
#     resolution_min = models.DecimalField(max_digits=7, decimal_places=2, default=4000.0)
#     resolution_max = models.DecimalField(max_digits=7, decimal_places=2, default=0.25)
#     published = models.BooleanField(default=False, help_text="Publication in GetCapabilities")
#     publication_service = models.ForeignKey('publication.WMTS', null=True, blank=True, on_delete=models.SET_NULL)


# class MapServerGroup(models.Model):
#     dataset = models.ForeignKey('layers.Dataset', on_delete=models.CASCADE)
#     mapserver_group_name = models.CharField(max_length=512, null=True, blank=True)
#     publication_services = models.ManyToManyField('publication.WMS')

#     @property
#     def name(self):
#         return self.mapserver_group_name or self.dataset.name


# class VersionedManager(models.Manager):
#     # Setting use_for_related_fields to True on the manager will make it
#     # available on all relations that point to the model on which you defined
#     # this manager as the default manager.
#     use_for_related_fields = True

#     def get_queryset(self):
#         return super().get_queryset().filter(current=True)



# class MapServerLayerManager(models.Manager):

#     def get_queryset(self):
#         return super().get_queryset().prefetch_related('group','group__dataset')


# class ExtentField(ArrayField):

#     def __init__(self, epsg=2056, *args, **kwargs):
#         self.epsg = epsg
#         # We need four coordinates
#         kwargs['size'] = 4
#         # Note: we have to pass the base_field as kwargs param
#         # and NOT as args param, __init__ is called repeately
#         # for ArrayField, the args base_field param is transformed
#         # to a kwargs param after the first iteration and results in a
#         # "got multiple values for argument 'base_field'" error at the
#         # second call
#         kwargs['base_field'] = models.IntegerField()
#         super().__init__(*args, **kwargs)

#     def to_python(self, value):
#         extent = super().to_python(value)

#         if self.epsg == 2056:
#             if extent[0] < 2100000 or extent[0] > 2850000:
#                 raise ValidationError('south west Easting must be between 2100000 and 2850000')
#             if extent[1] < 1050000 or extent[1] > 1400000:
#                 raise ValidationError('south west Northing must be between 1050000 and 1400000')
#             if extent[2] < 2100000 or extent[2] > 2850000:
#                 raise ValidationError('north east Easting must be between 2100000 and 2850000')
#             if extent[3] < 1050000 or extent[3] > 1400000:
#                 raise ValidationError('north east Northing must be between 1050000 and 1400000')
#             if extent[2] < extent[0]:
#                 raise ValidationError('eastern x bound ({}) must larger than western x bound ({})'.format(extent[2], extent[0]))
#             if extent[3] < extent[1]:
#                 raise ValidationError('eastern y bound ({}) must larger than western y bound ({})'.format(extent[2], extent[0]))

#         return extent



# class MapServerLayer(models.Model):

#     created = models.DateTimeField(default=timezone.now)
#     modified = models.DateTimeField(default=timezone.now)
#     group = models.ForeignKey(
#         'layers.MapServerGroup',
#         on_delete=models.CASCADE
#     )

#     mapserver_layer_name = models.CharField(max_length=512, null=True, blank=True)

#     mapfile = models.TextField()
#     mapfile_json = models.JSONField(blank=True)



#     UNITS_CHOICE_METERS = 'meters'
#     UNITS_CHOICES = (
#         (UNITS_CHOICE_METERS, _('meters')),
#     )
#     units = models.CharField(
#         max_length=32,
#         choices=UNITS_CHOICES,
#         default=UNITS_CHOICE_METERS
#     )

#     template = models.CharField(
#         max_length=512,
#         default='ttt'
#     )

#     status = models.BooleanField(default=True)
#     def get_status_display(self):
#         return 'ON' if self.status else 'OFF'

#     wms_extent = ExtentField(null=True)
#     wms_enable_request = models.CharField(max_length=128, default='*')

#     objects = MapServerLayerManager()

#     class Meta:
#         unique_together = (('group', 'mapserver_layer_name'),)


#     @property
#     def has_siblings(self):
#         return self.group.mapserverlayer_set.all().count() > 1


#     @property
#     def name(self):
#         return self.mapserver_layer_name or self.group.dataset.name

#     @property
#     def __type__(self):
#         return 'layer'

#     @property
#     def metadata(self):
#         dct = {}
#         dct['__type__'] = 'metadata'
#         dct['wms_title'] = self.group.dataset.name
#         dct['wms_extent'] = self.wms_extent
#         dct['wms_enable_request'] = self.wms_enable_request
#         return dct


#     def __str__(self):
#         return self.mapserver_layer_name or self.group.dataset.name

#     def clean(self):
#         """clean is called during .save() to validate the model fields"""
#         try:
#             parsed_mapfile = mappyfile.loads(self.mapfile)
#         except Exception as e:
#             raise ValidationError("couldn't parse mapfile content: {}".format(e))
#         else:
#             # print(parsed_mapfile)
#             self.mapfile_json = parsed_mapfile
#             self.mapfile_json['metadata']['wms_title'] = self.group.dataset.name
#             self.mapfile_json['metadata']['wms_timeextent'] = self.group.dataset.timing
#             self.mapfile_json['type'] = self.group.dataset.datatype.upper()
#             if self.group.dataset.srs:
#                 self.mapfile_json['projection'] = ["init={}".format(self.group.dataset.srs.epsg.lower())]
