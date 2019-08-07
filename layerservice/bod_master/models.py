from django.db import models

# Create your models here.

class Tileset(models.Model):

    fk_dataset_id = models.CharField(max_length=1024, null=False, db_column='fk_dataset_id') #   | character varying           | not null
    format = models.CharField(max_length=1024, null=True, db_column='format') #            | character varying           | 
    timestamp = models.CharField(max_length=1024, null=False, db_column='timestamp') #         | character varying           | not null
    bgdi_modified = models.DateTimeField(auto_now=True, db_column='bgdi_modified')#     | timestamp without time zone | 
    bgdi_created = models.DateTimeField(db_column='bgdi_created') #    | timestamp without time zone | 
    bgdi_modified_by = models.CharField(max_length=50, db_column='bgdi_modified_by', null=True) #  | character varying(50)       | 
    bgdi_created_by = models.CharField(max_length=50, db_column='bgdi_created_by', null=True) #  | character varying(50)       | 
    bgdi_id = models.PositiveIntegerField(db_column='bgdi_id', primary_key=True) #          | integer                     | not null default nextval('tileset_bgdi_id_seq'::regclass)
    wms_gutter = models.PositiveIntegerField(db_column='wms_gutter', default=0) #        | integer                     | not null default 0
    cache_ttl = models.PositiveIntegerField(db_column='cache_ttl', default=1800, help_text='Cache "time to live"') #       | integer                     | default 1800
    resolution_min = models.DecimalField(db_column='resolution_min', max_digits=7, decimal_places=2) #   | numeric                     | default 4000.0
    resolution_max = models.DecimalField(db_column='resolution_max', max_digits=7, decimal_places=2) #   | numeric                     | default 0.25
    published = models.BooleanField(db_column='published', default=True) #         | boolean                     | default true
    # s3_resolution_max = models.| numeric                     | 



    class Meta:
        managed = False
        db_table = 'tileset'

    def __str__(self):
        return self.fk_dataset_id


class Dataset(models.Model):

    # id colum is automatically added
    # id = models.TextField(db_column='id') #                                    | integer                     | not null default nextval('dataset_and_groups_id_seq'::regclass)      | plain    |              | 
    parent_id = models.TextField(db_column='parent_id', help_text="Technische Layer ID der Gruppe zu welcher eine oder mehrere datasets gehören, Einschränkung ein dataset kann zu maximal einer gruppe gehören.") #                             | text                        |                                                                      | extended |              | Technische Layer ID der Gruppe zu welcher eine oder mehrere datasets gehören, Einschränkung ein dataset kann zu maximal einer gruppe gehören.
    id_dataset = models.TextField(unique=True, db_column='id_dataset', null=False, help_text="Eindeutiger Name des datasets oder layer entsprechend Namenskonvention Layernamen, entspricht dem layername. ") #                            | text                        | not null                                                             | extended |              | Eindeutiger Name des datasets oder layer entsprechend Namenskonvention Layernamen, entspricht dem layername. 
    # frm_bezeichnung_de = models.TextField(db_column='frm_bezeichnung_de') #                    | text                        |                                                                      | extended |              | 
    # frm_bezeichnung_fr = models.TextField(db_column='frm_bezeichnung_fr') #                    | text                        |                                                                      | extended |              | 
    # frm_bezeichnung_it = models.TextField(db_column='frm_bezeichnung_it') #                    | text                        |                                                                      | extended |              | 
    # frm_bezeichnung_en = models.TextField(db_column='frm_bezeichnung_en') #                    | text                        |                                                                      | extended |              | 
    # frm_bezeichnung_rm = models.TextField(db_column='frm_bezeichnung_rm') #                    | text                        |                                                                      | extended |              | 
    # frm_abstract_de = models.TextField(db_column='frm_abstract_de') #                       | text                        |                                                                      | extended |              | 
    # frm_abstract_fr = models.TextField(db_column='frm_abstract_fr') #                       | text                        |                                                                      | extended |              | 
    # frm_abstract_it = models.TextField(db_column='frm_abstract_it') #                       | text                        |                                                                      | extended |              | 
    # frm_abstract_en = models.TextField(db_column='frm_abstract_en') #                       | text                        |                                                                      | extended |              | 
    # frm_abstract_rm = models.TextField(db_column='frm_abstract_rm') #                       | text                        |                                                                      | extended |              | 
    # kurzbezeichnung_de = models.TextField(db_column='kurzbezeichnung_de') #                    | text                        |                                                                      | extended |              | 
    # kurzbezeichnung_fr = models.TextField(db_column='kurzbezeichnung_fr') #                    | text                        |                                                                      | extended |              | 
    # kurzbezeichnung_it = models.TextField(db_column='kurzbezeichnung_it') #                    | text                        |                                                                      | extended |              | 
    # kurzbezeichnung_en = models.TextField(db_column='kurzbezeichnung_en') #                    | text                        |                                                                      | extended |              | 
    # kurzbezeichnung_rm = models.TextField(db_column='kurzbezeichnung_rm') #                    | text                        |                                                                      | extended |              | 
    frm_nachfuehrung_intervall = models.TextField(db_column='frm_nachfuehrung_intervall', default='andere') #            | text                        | not null default 'andere'::text                                      | extended |              | 
    frm_scale_limit = models.TextField(db_column='frm_scale_limit', default='-') #                       | text                        | not null default '-'::text                                           | extended |              | 
    ms_minscaledenom = models.IntegerField(db_column='ms_minscaledenom') #                      | integer                     |                                                                      | plain    |              | wms-bgdi / Geoadmin Spezifische MapFileParameter                                                                                             +
    ms_maxscaledenom = models.IntegerField(db_column='ms_maxscaledenom') #                      | integer                     |                                                                      | plain    |              | wms-bgdi / Geoadmin Spezifische MapFileParameter                                                                                             +
    ms_labelminscaledenom = models.IntegerField(db_column='ms_labelminscaledenom', default=-1) #                 | integer                     | default '-1'::integer                                                | plain    |              | wms-bgdi / Geoadmin Spezifische MapFileParameter                                                                                             +
    ms_labelmaxscaledenom = models.IntegerField(db_column='ms_labelmaxscaledenom', default=-1) #                 | integer                     | default '-1'::integer                                                | plain    |              | wms-bgdi / Geoadmin Spezifische MapFileParameter                                                                                             +
    # frm_url = models.TextField(db_column='frm_url', help_text="Informations URL aus dem Datenintegrations Formular") #                               | text                        |                                                                      | extended |              | Informations URL aus dem Datenintegrations Formular
    # b1_nutzungsbedingungen = models.TextField(db_column='b1_nutzungsbedingungen', help_text="URL zu den Nutzungsbedingungen") #                | text                        |                                                                      | extended |              | URL zu den Nutzungsbedingungen
    b1_urheberrecht = models.TextField(db_column='b1_urheberrecht') #                       | text                        |                                                                      | extended |              | 
    # url_download = models.TextField(db_column='url_download', help_text="URL zum Download Dienst") #                          | text                        |                                                                      | extended |              | URL zum Download Dienst
    # url_portale = models.TextField(db_column='url_portale', help_text="Liste mit URLs von Portalen die diesen Datensatz verwenden.") #                           | text                        |                                                                      | extended |              | Liste mit URLs von Portalen die diesen Datensatz verwenden.
    # fk_geobasisdaten_sammlung_bundesrecht = models.TextField(db_column='fk_geobasisdaten_sammlung_bundesrecht') # | text                        |                                                                      | extended |              | 
    fk_geocat = models.TextField(db_column='fk_geocat', help_text="referencing regular grid raster extent") #                             | text                        |                                                                      | extended |              | referencing regular grid raster extent
    fk_datasource_id = models.TextField(db_column='fk_datasource_id') #                      | text                        |                                                                      | extended |              | 
    fk_contactorganisation_id = models.IntegerField(db_column='fk_contactorganisation_id') #             | integer                     |                                                                      | plain    |              | 
    comment = models.TextField(db_column='comment') #                               | text                        | default ''::text                                                     | extended |              | 
    staging = models.TextField(db_column='staging', default='test') #                               | text                        | default 'test'::text                                                 | extended |              | 
    bodsearch = models.BooleanField(db_column='bodsearch', help_text="bodsearch true/false set true if layer should be visible in chsdi layers, feature, bodsearch.") #                             | boolean                     | not null default false                                               | plain    |              | bodsearch true/false set true if layer should be visible in chsdi layers, feature, bodsearch.
    bgdi_id = models.IntegerField(db_column='bgdi_id') #                               | integer                     | not null default nextval('dataset_and_groups_bgdi_id_seq'::regclass) | plain    |              | 
    download = models.BooleanField(db_column='download', default=False, help_text="chargeable true/false if layer wmts access is chargeable or not") #                              | boolean                     | not null default false                                               | plain    |              | chargeable true/false if layer wmts access is chargeable or not
    bgdi_modified = models.DateTimeField(db_column='bgdi_modified', auto_now=True) #                         | timestamp without time zone |                                                                      | plain    |              | 
    bgdi_created = models.DateTimeField(db_column='bgdi_created', auto_now_add=True) #                          | timestamp without time zone |                                                                      | plain    |              | 
    bgdi_modified_by = models.CharField(max_length=50, db_column='bgdi_modified_by') #                      | character varying(50)       |                                                                      | extended |              | 
    bgdi_created_by = models.CharField(max_length=50, db_column='bgdi_created_by') #                       | character varying(50)       |                                                                      | extended |              | 
    ows_keywordlist_de = models.TextField(db_column='ows_keywordlist_de') #                    | text                        |                                                                      | extended |              | 
    ows_keywordlist_fr = models.TextField(db_column='ows_keywordlist_fr') #                    | text                        |                                                                      | extended |              | 
    ows_keywordlist_it = models.TextField(db_column='ows_keywordlist_it') #                    | text                        |                                                                      | extended |              | 
    ows_keywordlist_en = models.TextField(db_column='ows_keywordlist_en') #                    | text                        |                                                                      | extended |              | 
    ows_keywordlist_rm = models.TextField(db_column='ows_keywordlist_rm') #                    | text                        |                                                                      | extended |              | 
    chargeable = models.BooleanField(db_column='chargeable', default=False) #                            | boolean                     | not null default false                                               | plain    |              |

    def __str__(self):
        return self.id_dataset

    class Meta:
        managed = False
        db_table = 'dataset'


class GeocatPublish(models.Model):
    fk_id_dataset = models.OneToOneField('Dataset',
        db_column='fk_id_dataset',
        primary_key=True,
        to_field='id_dataset',
        on_delete=models.CASCADE
    )  #          | text                        | not null
    bezeichnung_de = models.TextField()  #         | text                        | 
    bezeichnung_fr = models.TextField()  #         | text                        | 
    bezeichnung_it = models.TextField()  #         | text                        | 
    bezeichnung_en = models.TextField()  #         | text                        | 
    bezeichnung_rm = models.TextField()  #         | text                        | 
    alternativtitel_de = models.TextField()  #     | text                        | 
    alternativtitel_fr = models.TextField()  #     | text                        | 
    alternativtitel_it = models.TextField()  #     | text                        | 
    alternativtitel_en = models.TextField()  #     | text                        | 
    alternativtitel_rm = models.TextField()  #     | text                        | 
    abstract_de = models.TextField()  #            | text                        | 
    abstract_fr = models.TextField()  #            | text                        | 
    abstract_it = models.TextField()  #            | text                        | 
    abstract_en = models.TextField()  #            | text                        | 
    abstract_rm = models.TextField()  #            | text                        | 
    nutzungsbedingungen_de = models.CharField(max_length=300)  # | character varying(300)      | 
    nutzungsbedingungen_fr = models.CharField(max_length=300)  # | character varying(300)      | 
    nutzungsbedingungen_it = models.CharField(max_length=300)  # | character varying(300)      | 
    nutzungsbedingungen_en = models.CharField(max_length=300)  # | character varying(300)      | 
    nutzungsbedingungen_rm = models.CharField(max_length=300)  # | character varying(300)      | 
    fk_geobasisdatensatz = models.TextField()  #   | text                        | 
    url_infos = models.TextField()  #              | text                        | 
    url_download = models.TextField()  #           | text                        | 
    url_portal = models.TextField()  #             | text                        | 
    bgdi_modified = models.DateTimeField()  #          | timestamp without time zone | 
    bgdi_created = models.DateTimeField()  #           | timestamp without time zone | 
    bgdi_modified_by = models.CharField(max_length=50)  #       | character varying(50)       | 
    bgdi_created_by = models.CharField(max_length=50)  #        | character varying(50)       | 
    bgdi_id = models.IntegerField()  #                | integer                     | not null default nextval('geocat_publish_bgdi_id_seq'::regclass)

    def __str__(self):
        return self.fk_id_dataset.id_dataset

    class Meta:
        managed = False
        db_table = 'geocat_publish'


class LayersJS(models.Model):
    # Demonstrate how to access Table in different schema

    bgdi_id = models.IntegerField(db_column="bgdi_id", primary_key=True) #             | integer                     | not null default nextval('layers_js_bgdi_id_seq'::regclass) | plain    |              | 
    fk_parent_layer = models.TextField(db_column="fk_parent_layer") #     | text                        |                                                             | extended |              | 
    pk_layer = models.TextField(db_column="pk_layer") #            | text                        | not null                                                    | extended |              | 
    fk_id_dataset = models.TextField(db_column="fk_id_dataset") #       | text                        |                                                             | extended |              | 
    LAYERTYPE_AGGREGATE = 'aggregate'
    LAYERTYPE_GEOJSON = 'geojson'
    LAYERTYPE_WMS = 'wms'
    LAYERTYPE_WMTS = 'wmts'
    LAYERTYPE_CHOICES = (
        (LAYERTYPE_AGGREGATE, 'aggregate'),
        (LAYERTYPE_GEOJSON, 'geojson'),
        (LAYERTYPE_WMS, 'wms'),
        (LAYERTYPE_WMTS, 'wmts')
    )
    layertype = models.CharField(choices=LAYERTYPE_CHOICES, max_length=50, db_column="layertype") #           | text                        | not null                                                    | extended |              | 
    opacity = models.FloatField(db_column="opacity") #             | double precision            |                                                             | plain    |              | 
    minresolution = models.FloatField(db_column="minresolution") #       | double precision            |                                                             | plain    |              | 
    maxresolution = models.FloatField(db_column="maxresolution") #       | double precision            |                                                             | plain    |              | 
    image_format = models.TextField(db_column="image_format") #        | text                        |                                                             | extended |              | 
    wms_layers = models.TextField(db_column="wms_layers") #          | text                        |                                                             | extended |              | 
    fk_wms_metadata = models.TextField(db_column="fk_wms_metadata") #     | text                        |                                                             | extended |              | 
    backgroundlayer = models.BooleanField(db_column="backgroundlayer") #     | boolean                     | not null default false                                      | plain    |              | 
    searchable = models.BooleanField(db_column="searchable") #          | boolean                     | not null default false                                      | plain    |              | 
    timeenabled = models.BooleanField(db_column="timeenabled") #         | boolean                     | not null default false                                      | plain    |              | 
    haslegend = models.BooleanField(db_column="haslegend") #           | boolean                     | not null default true                                       | plain    |              | 
    singletile = models.BooleanField(db_column="singletile") #          | boolean                     | not null default true                                       | plain    |              | 
    bgdi_modified = models.DateTimeField(db_column="bgdi_modified", auto_now=True) #       | timestamp without time zone |                                                             | plain    |              | 
    bgdi_created = models.DateTimeField(db_column="bgdi_created", auto_now_add=True) #        | timestamp without time zone |                                                             | plain    |              | 
    bgdi_modified_by = models.CharField(max_length=50, db_column="bgdi_modified_by") #    | character varying(50)       |                                                             | extended |              | 
    bgdi_created_by = models.CharField(max_length=50, db_column="bgdi_created_by") #     | character varying(50)       |                                                             | extended |              | 
    highlightable = models.BooleanField(db_column="highlightable") #       | boolean                     | default true                                                | plain    |              | 
    time_get_parameter = models.TextField(db_column="time_get_parameter") #  | text                        |                                                             | extended |              | time enabled wms layers                                                     +
    #                            |                                                             |          |              | name of the get parameter in the time enabled wms get map query
    time_format = models.TextField(db_column="time_format") #         | text                        |                                                             | extended |              | time enabled wms layers                                                     +
    #                            |                                                             |          |              | pattern / format of the time dimension in the time enabled wms get map query+
    #                            |                                                             |          |              |                                                                             +
    #                            |                                                             |          |              | p.e.                                                                        +
    #                            |                                                             |          |              | YYYY                                                                        +
    #                            |                                                             |          |              | YYYY-MM                                                                     +
    #                            |                                                             |          |              | YYYY-MM-DD
    time_behaviour = models.TextField(db_column="time_behaviour") #      | text                        | not null default 'last'::text                               | extended |              | 
    wms_gutter = models.IntegerField(db_column="wms_gutter") #          | integer                     |                                                             | plain    |              | 
    geojson_url_de = models.TextField(db_column="geojson_url_de") #      | text                        |                                                             | extended |              | 
    geojson_url_fr = models.TextField(db_column="geojson_url_fr") #      | text                        |                                                             | extended |              | 
    geojson_url_it = models.TextField(db_column="geojson_url_it") #      | text                        |                                                             | extended |              | 
    geojson_url_en = models.TextField(db_column="geojson_url_en") #      | text                        |                                                             | extended |              | 
    geojson_url_rm = models.TextField(db_column="geojson_url_rm") #      | text                        |                                                             | extended |              | 
    geojson_update_delay = models.IntegerField(db_column="geojson_update_delay") #| integer                     |                                                             | plain    |              | geoJSON automatic update interval, in milliseconds
    tooltip = models.BooleanField(db_column="tooltip") #             | boolean                     | not null default false                                      | plain    |              | 
    shop_option_arr = models.TextField(db_column="shop_option_arr") #     | text[]                      |                                                             | extended |              | Contains a list of possible selection methods for purchase
    srid = models.CharField(max_length=40, default="2056", db_column="srid") #                | text                        | not null default (2056)::text                               | extended |              | 
    fk_config3d = models.TextField(db_column="fk_config3d") #         | text                        |                                                             | extended |              | 
    extent = models.FloatField(db_column="extent") #              | double precision[]          |                                                             | extended |              | 

    class Meta:
        managed = False
        db_table = 'layers_js'


class LayersJSView(models.Model):


    bgdi_id = models.IntegerField(db_column="bgdi_id", primary_key=True)  #                   | integer            |           | plain    |              | 
    layer_id = models.TextField(db_column="layer_id")  #                  | text               |           | extended |              | 
    bod_layer_id = models.TextField(db_column="bod_layer_id")  #              | text               |           | extended |              | 
    topics = models.TextField(db_column="topics")  #                    | text               |           | extended |              | 
    chargeable = models.BooleanField(db_column="chargeable")  #                | boolean            |           | plain    |              | 
    staging = models.TextField(db_column="staging")  #                   | text               |           | extended |              | 
    server_layername = models.TextField(db_column="server_layername")  #          | text               |           | extended |              | 
    attribution = models.TextField(db_column="attribution")  #               | text               |           | extended |              | 
    layertype = models.TextField(db_column="layertype")  #                 | text               |           | extended |              | 
    opacity = models.FloatField(db_column="opacity")  #                   | double precision   |           | plain    |              | 
    minresolution = models.FloatField(db_column="minresolution")  #             | double precision   |           | plain    |              | 
    maxresolution = models.FloatField(db_column="maxresolution")  #             | double precision   |           | plain    |              | 
    extent = models.FloatField(db_column="extent")  #                    | double precision[] |           | extended |              | 
    backgroundlayer = models.BooleanField(db_column="backgroundlayer")  #           | boolean            |           | plain    |              | 
    tooltip = models.BooleanField(db_column="tooltip")  #                   | boolean            |           | plain    |              | 
    searchable = models.BooleanField(db_column="searchable")  #                | boolean            |           | plain    |              | 
    timeenabled = models.BooleanField(db_column="timeenabled")  #               | boolean            |           | plain    |              | 
    haslegend = models.BooleanField(db_column="haslegend")  #                 | boolean            |           | plain    |              | 
    singletile = models.BooleanField(db_column="singletile")  #                | boolean            |           | plain    |              | 
    highlightable = models.BooleanField(db_column="highlightable")  #             | boolean            |           | plain    |              | 
    wms_layers = models.TextField(db_column="wms_layers")  #                | text               |           | extended |              | 
    time_behaviour = models.TextField(db_column="time_behaviour")  #            | text               |           | extended |              | 
    image_format = models.TextField(db_column="image_format")  #              | text               |           | extended |              | 
    tilematrix_resolution_max = models.FloatField(db_column="tilematrix_resolution_max")  # | double precision   |           | plain    |              | 
    timestamps = models.TextField(db_column="timestamps")  #                | text[]             |           | extended |              | 
    parentlayerid = models.TextField(db_column="parentlayerid")  #             | text               |           | extended |              | 
    sublayersids = models.TextField(db_column="sublayersids")  #              | text[]             |           | extended |              | 
    time_get_parameter = models.TextField(db_column="time_get_parameter")  #        | text               |           | extended |              | 
    time_format = models.TextField(db_column="time_format")  #               | text               |           | extended |              | 
    wms_gutter = models.IntegerField(db_column="wms_gutter")  #                | integer            |           | plain    |              | 
    sphinx_index = models.TextField(db_column="sphinx_index")  #              | text               |           | extended |              | 
    geojson_url_de = models.TextField(db_column="geojson_url_de")  #            | text               |           | extended |              | 
    geojson_url_fr = models.TextField(db_column="geojson_url_fr")  #            | text               |           | extended |              | 
    geojson_url_it = models.TextField(db_column="geojson_url_it")  #            | text               |           | extended |              | 
    geojson_url_en = models.TextField(db_column="geojson_url_en")  #            | text               |           | extended |              | 
    geojson_url_rm = models.TextField(db_column="geojson_url_rm")  #            | text               |           | extended |              | 
    geojson_update_delay = models.IntegerField(db_column="geojson_update_delay")  #      | integer            |           | plain    |              | 
    shop_option_arr = models.TextField(db_column="shop_option_arr")  #           | text[]             |           | extended |              | 
    srid = models.TextField(db_column="srid")  #                      | text               |           | extended |              | 
    fk_config3d = models.TextField(db_column="fk_config3d")  #               | text               |           | extended |              | 
                         
    class Meta:
        managed = False
        db_table = 'view_layers_js'


class Topic(models.Model):
    
    topic = models.TextField(db_column="topic") #                   | text                        | not null                                                 | extended |              | 
    bgdi_id = models.IntegerField(db_column="bgdi_id", primary_key=True) #                 | integer                     | not null default nextval('topics_bgdi_id_seq'::regclass) | plain    |              | 
    default_background = models.TextField(db_column="default_background") #      | text                        |                                                          | extended |              | 
    selected_layers = models.TextField(db_column="selected_layers") #         | text[]                      | not null default '{}'::text[]                            | extended |              | 
    background_layers = models.TextField(db_column="background_layers") #       | text[]                      | not null default '{}'::text[]                            | extended |              | 
    staging = models.TextField(db_column="staging") #                 | text                        | default 'test'::text                                     | extended |              | 
    show_catalog = models.BooleanField(db_column="show_catalog") #            | boolean                     | not null default false                                   | plain    |              | 
    bgdi_modified = models.DateTimeField(db_column="bgdi_modified") #           | timestamp without time zone |                                                          | plain    |              | 
    bgdi_created = models.DateTimeField(db_column="bgdi_created") #            | timestamp without time zone |                                                          | plain    |              | 
    bgdi_modified_by = models.CharField(max_length=50, db_column="bgdi_modified_by") #        | character varying(50)       |                                                          | extended |              | 
    bgdi_created_by = models.CharField(max_length=50, db_column="bgdi_created_by") #         | character varying(50)       |                                                          | extended |              | 
    activated_layers = models.TextField(db_column="activated_layers") #        | text[]                      | not null default '{}'::text[]                            | extended |              | 
    permalink_configuration = models.TextField(db_column="permalink_configuration") # | text                        |                                                          | extended |              | 
    group_id = models.IntegerField(db_column="group_id") #                | integer                     |                                                          | plain    |              | 

    class Meta:
        managed = False
        db_table = 'topics'


class Catalog(models.Model):

    bgdi_id = models.IntegerField(db_column="bgdi_id", primary_key=True)           # | 819000
    catalog_parent_id = models.IntegerField() # | 1
    catalog_id = models.IntegerField()        # | 2
    topic = models.CharField(max_length=512)             # | inspire
    name_de = models.CharField(max_length=512)           # | Koordinatenreferenzsysteme
    name_fr = models.CharField(max_length=512)           # | Référentiels de coordonnées
    name_it = models.CharField(max_length=512)           # | Sistemi di coordinate
    name_en = models.CharField(max_length=512)           # | Coordinate reference systems
    name_rm = models.CharField(max_length=512)           # | Sistems da referenza da coordinatas
    order_key = models.IntegerField()         # | 1
    selected_open = models.BooleanField()     # | f
    staging = models.CharField(max_length=512)           # | prod
    bgdi_modified = models.CharField(max_length=512)     # | 
    bgdi_created = models.CharField(max_length=512)      # | 2017-01-31 09:38:36.532727
    bgdi_modified_by = models.CharField(max_length=512)  # | 
    bgdi_created_by = models.CharField(max_length=512)   # | pgkogis

    class Meta:
        managed = False
        db_table = 'catalog'

class XTDatasetCatalog(models.Model):
    bgdi_id = models.IntegerField(db_column="bgdi_id", primary_key=True) #          | 7650
    fk_dataset = models.CharField(max_length=512) #       | ch.bazl.luftraeume-kontrollzonen
    fk_topic = models.CharField(max_length=512) #         | dev
    bgdi_modified = models.DateTimeField() #    | 2017-02-03 17:14:44.792226
    bgdi_created = models.DateTimeField() #     | 2016-10-25 15:44:54.95772
    bgdi_modified_by = models.CharField(max_length=512) # | bod_admin
    bgdi_created_by = models.CharField(max_length=512) #  | pgkogis
    catalog_id = models.IntegerField() #       | 501
    order_key = models.IntegerField() #        | 0

    class Meta:
        managed = False
        db_table = 'xt_dataset_catalog'


class XTDatasetTopic(models.Model):
    fk_dataset = models.CharField(max_length=512) #       | ch.bafu.gefahren-aktuelle_erdbeben
    fk_topic = models.CharField(max_length=512) #         | inspire
    bgdi_id = models.IntegerField(db_column="bgdi_id", primary_key=True) #          | 1033720
    bgdi_modified = models.DateTimeField() #    | 
    bgdi_created = models.DateTimeField() #     | 2017-02-07 07:46:45.809892
    bgdi_modified_by = models.CharField(max_length=512) # | 
    bgdi_created_by = models.CharField(max_length=512) #  | pgkogis

    class Meta:
        managed = False
        db_table = 'xt_dataset_topics'

