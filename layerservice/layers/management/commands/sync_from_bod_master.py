import logging
import dateutil.parser

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.utils.dateparse import parse_datetime
from django.utils import timezone

import mptt

from layers.models import Tileset, Dataset
from catalog.models import Topic, CatalogLayer, CatalogEntry
from bod_master.models import Tileset as bod_master_Tileset
from bod_master.models import Dataset as bod_master_Dataset
from bod_master.models import Topic as bod_master_Topic
from bod_master.models import Catalog as bod_master_Catalog
from bod_master.models import XTDatasetCatalog as bod_master_XTDatasetCatalog
from translation.models import TranslationKey, Translation


logger = logging.getLogger('default')

def increment_suffix(s, separator='_'):
    parts = s.split(separator)
    try:
        suffix = int(parts[-1])
    except ValueError:
        # last part of the string is not an int
        suffix = "{}_1".format(parts[-1])
    else:
        suffix += 1
    parts[-1] = str(suffix)
    return separator.join(parts)


TRANSLATION_KEY_MAX_LENGTH = 50


class Command(BaseCommand):
    help = 'Syncs bod_master data with layers models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topics',
            action='store_true',
            help='Sync topics'
        )
        parser.add_argument(
            '--datasets',
            action='store_true',
            help='Sync datasets'
        )

    def handle(self, *args, **options):
        if options['topics']:
            for bodm_topic in bod_master_Topic.objects.all():
                topic, created = Topic.objects.get_or_create(
                    name=bodm_topic.topic
                    )
                if created:
                    print("created new topic {}".format(bodm_topic.topic))
                topic.staging = bodm_topic.staging

                for bodm_catalog in bod_master_Catalog.objects.filter(topic=topic.name).order_by('-catalog_id'):
                    parent = None
                    if bodm_catalog.catalog_parent_id:
                        # print("entry has parent, try to find, if not, continue")
                        try:
                            parent = CatalogEntry.objects.get(bodm_legacy_catalog_id=bodm_catalog.catalog_parent_id)
                        except CatalogEntry.DoesNotExist as e:
                            print("parent of {} with id {} doesn't exists (yet), continueing".format(bodm_catalog.catalog_id, bodm_catalog.catalog_parent_id))
                            continue
                            


                    catalogentry, create = CatalogEntry.objects.get_or_create(
                        bodm_legacy_catalog_id=bodm_catalog.catalog_id,
                        defaults={
                            'topic': topic
                        }
                    )
                    # print("bodm_catalog.catalog_parent_id",bodm_catalog.catalog_parent_id)
                    
                    if parent:
                        catalogentry.parent = parent

                    catalogentry.topic = topic
                    
                    if bodm_catalog.name_de:
                        catalogentry_name_slug = slugify(bodm_catalog.name_de)
                    else:
                        catalogentry_name_slug = slugify("{}_root".format(topic))
                    catalogentry.name = catalogentry.create_or_update_translations(
                        catalogentry_name_slug,
                        de=bodm_catalog.name_de,
                        fr=bodm_catalog.name_fr,
                        en=bodm_catalog.name_en,
                        it=bodm_catalog.name_it,
                        rm=bodm_catalog.name_rm
                    )
                    # catalogentry.activated = 

                    try:
                        catalogentry.save()
                    except mptt.exceptions.InvalidMove:
                        print("something is terribly wrong: {} cant be its own child".format(catalogentry))
                        continue

                    for bodm_xtdatasetcatalog in bod_master_XTDatasetCatalog.objects.filter(catalog_id=catalogentry.bodm_legacy_catalog_id):
                        try:
                            dataset = Dataset.objects.get(layer_name=bodm_xtdatasetcatalog.fk_dataset)
                        except Dataset.DoesNotExist:
                            pass
                        else:
                            activated = dataset.layer_name in bodm_topic.selected_layers
                            cataloglayer, created = CatalogLayer.objects.get_or_create(
                                catalog_entry=catalogentry,
                                dataset=dataset
                            )
                            cataloglayer.activated=activated
                            cataloglayer.save()


                topic.save()

        if options['datasets']:
            for bod_master_dataset in bod_master_Dataset.objects.all():
                dataset_id = bod_master_dataset.id_dataset

                # fetch or create the dataset with this id
                dataset, created = Dataset.objects.get_or_create(layer_name=dataset_id)
                if created:
                    print("created new dataset {}".format(dataset_id))

                # ========
                # Abstract
                if not dataset.abstract and hasattr(bod_master_dataset, 'geocatpublish'):                

                    # in case abstract_id is none use dataset_id
                    if not bod_master_dataset.geocatpublish.alternativtitel_en:
                        abstract_id = "{}_abstract".format(dataset_id)
                    else:
                        abstract_id = slugify(bod_master_dataset.geocatpublish.alternativtitel_en[:TRANSLATION_KEY_MAX_LENGTH])

                    while(TranslationKey.objects.filter(id=abstract_id).exists()):
                        abstract_id = increment_suffix(abstract_id)
                else:
                    abstract_id = dataset.abstract_id

                if hasattr(bod_master_dataset, 'geocatpublish'):
                    dataset.abstract = dataset.create_or_update_translations(
                        abstract_id,
                        de=bod_master_dataset.geocatpublish.alternativtitel_de,
                        fr=bod_master_dataset.geocatpublish.alternativtitel_fr,
                        it=bod_master_dataset.geocatpublish.alternativtitel_it,
                        en=bod_master_dataset.geocatpublish.alternativtitel_en,
                        rm=bod_master_dataset.geocatpublish.alternativtitel_rm,
                    )

                # ===========
                # Description
                if not dataset.description and hasattr(bod_master_dataset, 'geocatpublish'):

                    # in case description_id is none use dataset_id
                    if not bod_master_dataset.geocatpublish.bezeichnung_en:
                        description_id = "{}_description".format(dataset_id)
                    else:
                        description_id = slugify(bod_master_dataset.geocatpublish.bezeichnung_en[:TRANSLATION_KEY_MAX_LENGTH])

                    while(TranslationKey.objects.filter(id=description_id).exists()):
                        description_id = increment_suffix(description_id)
                else:
                    description_id = dataset.description_id

                if hasattr(bod_master_dataset, 'geocatpublish'):
                    dataset.description = dataset.create_or_update_translations(
                        description_id,
                        de = bod_master_dataset.geocatpublish.bezeichnung_de,
                        fr = bod_master_dataset.geocatpublish.bezeichnung_fr,
                        it = bod_master_dataset.geocatpublish.bezeichnung_it,
                        en = bod_master_dataset.geocatpublish.bezeichnung_en,
                        rm = bod_master_dataset.geocatpublish.bezeichnung_rm,
                    )

                dataset.chargeable = bod_master_dataset.chargeable

                dataset.save()

                for bod_master_tileset in bod_master_Tileset.objects.filter(fk_dataset_id=dataset_id):
                    if  bod_master_tileset.timestamp == 'current':
                        _timestamp = '9999-01-01'
                    elif len(bod_master_tileset.timestamp) == 4:
                        _timestamp = '{}-01-01'.format(bod_master_tileset.timestamp)
                    else:
                        _timestamp = bod_master_tileset.timestamp
                    tz_unaware_timestamp = dateutil.parser.parse(_timestamp)

                    timestamp = timezone.make_aware(tz_unaware_timestamp) if tz_unaware_timestamp else timezone.now()
                    print(bod_master_tileset.timestamp, timestamp)
                    tileset, created = Tileset.objects.get_or_create(
                        dataset=dataset,
                        timestamp=timestamp,
                    )
                    tileset.format = bod_master_tileset.format
                    tileset.cache_ttl = bod_master_tileset.cache_ttl
                    tileset.resolution_min = bod_master_tileset.resolution_min
                    tileset.resolution_max = bod_master_tileset.resolution_max
                    tileset.published = bod_master_tileset.published
                    tileset.save()