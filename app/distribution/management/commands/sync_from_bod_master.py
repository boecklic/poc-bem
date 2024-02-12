import re
import os
import logging
import dateutil.parser
import subprocess
import ast

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.utils.dateparse import parse_datetime
from django.utils import timezone

import mptt

from distribution.models import Dataset
from provider.models import Provider, Attribution
from bod_master.models import BODDataset, BODContactorganisation
from translation.models import Translation, create_or_update_translations, generate_key



logger = logging.getLogger('default')



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
        parser.add_argument(
            '--attributions',
            action='store_true',
            help='Sync attributions'
        )
        parser.add_argument(
            '--featurecollections',
            action='store_true',
            help='Sync Feature Collections'
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
                    catalogentry.name = create_or_update_translations(
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
                            dataset = Dataset.objects.get(name=bodm_xtdatasetcatalog.fk_dataset)
                        except Dataset.DoesNotExist:
                            pass
                        else:
                            activated = dataset.name in bodm_topic.selected_layers
                            cataloglayer, created = CatalogLayer.objects.get_or_create(
                                catalog_entry=catalogentry,
                                dataset=dataset
                            )
                            cataloglayer.activated=activated
                            cataloglayer.save()


                topic.save()

        if options['datasets']:
            for bod_master_dataset in BODDataset.objects.all():
                dataset_id = bod_master_dataset.id_dataset

                # fetch or create the dataset with this id
                dataset, created = Dataset.objects.get_or_create(name=dataset_id)
                if created:
                    print("created new dataset {}".format(dataset_id))

                if not dataset.provider:
                    print(f'--WARN dataset {dataset.name} doesn\'t have a provider')
                elif not dataset.name.startswith(dataset.provider.prefix):
                    print(f'--WARN dataset name {dataset.name} doens\'t start with provider prefix {dataset.provider.prefix}')

                # ========
                # Abstract
                if hasattr(bod_master_dataset, 'geocatpublish'):
                    if not bod_master_dataset.geocatpublish.alternativtitel_en:
                        slug_proposal = dataset_id
                    else:
                        slug_proposal = bod_master_dataset.geocatpublish.alternativtitel_en
                    abstract_key = generate_key(dataset.abstract, slug_proposal, prefix="abstract_")

                    dataset.abstract = create_or_update_translations(
                        abstract_key,
                        de=bod_master_dataset.geocatpublish.alternativtitel_de,
                        fr=bod_master_dataset.geocatpublish.alternativtitel_fr,
                        it=bod_master_dataset.geocatpublish.alternativtitel_it,
                        en=bod_master_dataset.geocatpublish.alternativtitel_en,
                        rm=bod_master_dataset.geocatpublish.alternativtitel_rm,
                    )

                # ===========
                # Description
                if hasattr(bod_master_dataset, 'geocatpublish'):

                    if not bod_master_dataset.geocatpublish.bezeichnung_en:
                        slug_proposal = dataset_id
                    else:
                        slug_proposal = bod_master_dataset.geocatpublish.bezeichnung_en
                    description_key = generate_key(dataset.description, slug_proposal, prefix="description_")


                    dataset.description = create_or_update_translations(
                        description_key,
                        de = bod_master_dataset.geocatpublish.bezeichnung_de,
                        fr = bod_master_dataset.geocatpublish.bezeichnung_fr,
                        it = bod_master_dataset.geocatpublish.bezeichnung_it,
                        en = bod_master_dataset.geocatpublish.bezeichnung_en,
                        rm = bod_master_dataset.geocatpublish.bezeichnung_rm,
                    )


                dataset.geocat_id = bod_master_dataset.fk_geocat
                try:
                    attribution = Attribution.objects.get(id=bod_master_dataset.fk_contactorganisation_id)
                    dataset.attribution = attribution
                    dataset.provider = attribution.provider
                except:
                    pass

                try:
                    dataset.save()
                except:
                    print(f"DUPLICATE: {bod_master_dataset.id_dataset} | {bod_master_dataset.fk_geocat}")
                    continue

            # Create a dataset that serves as container for all collections that don't have a dataset
            noatt = Attribution.objects.get(id=1000)
            orphaned, created = Dataset.objects.get_or_create(name="ORPHANED", attribution=noatt, provider=noatt.provider)


        if options['attributions']:

            provider_list = [
                ("BLW","blw"),
                ("swisstopo","swisstopo"),
                ("BAFU","bafu"),
                ("ASTRA","astra"),
                ("BFS","bfs"),
                ("BABS","babs"),
                ("ARE","are"),
                ("tamedia","tamedia"),
                ("ENSI","ensi"),
                ("VBS","vbs"),
                ("BAKOM","bakom"),
                ("BAZL","bazl"),
                ("BFE","bfe"),
                ("BAK","bak"),
                ("BAV","bav"),
                ("LW","lw"),
                ("BAG","bag"),
                ("AV","av"),
                ("Pro Natura","pronatura"),
                ("SED / ETH Zürich","sed"),
                ("NAGRA","nagra"),
                ("Mobility","mobility"),
                ("BAZG","bazg"),
                ("SEM","sem"),
                ("MeteoSchweiz","meteoschweiz"),
                ("BASPO","baspo"),
                ("Agroscope","agroscope"),
                ("armasuisse","armasuisse"),
                ("GS-VBS","gs-vbs"),
                ("Schweizer Armee","armee"),
                ("NO PROVIDER","nopro")
            ]
            for provider in provider_list:
                provider, created = Provider.objects.get_or_create(name=provider[0], prefix=f'ch.{provider[1]}')
                if created:
                    print("created new provider {}".format(provider))


            for bod_master_attribution in BODContactorganisation.objects.all():
                id = bod_master_attribution.pk_contactorganisation_id
                provider = None
                for provider_name, prefix in provider_list:
                    if provider_name in bod_master_attribution.abkuerzung_de:
                        try:
                            provider = Provider.objects.get(name=provider_name)
                        except Exception as e:
                            print(f'--WARN {provider_name} doesn\'t exist')
                if not provider:
                    provider = Provider.objects.get(name=provider_list[-1][0])

                # fetch or create the attribution with this id
                attribution, created = Attribution.objects.get_or_create(id=id, provider=provider)
                if created:
                    print("created new attribution {}".format(attribution.id))

                # ========
                # Name

                name_key = generate_key(attribution.name, bod_master_attribution.name_de, prefix="attribution_name_")

                attribution.name = create_or_update_translations(
                    name_key,
                    de=bod_master_attribution.name_de,
                    fr=bod_master_attribution.name_fr,
                    en=bod_master_attribution.name_en,
                    it=bod_master_attribution.name_it,
                    rm=bod_master_attribution.name_rm,
                )

                # ========
                # Short

                short_key = generate_key(attribution.short, bod_master_attribution.abkuerzung_de, prefix="attribution_short_")

                attribution.short = create_or_update_translations(
                    short_key,
                    de=bod_master_attribution.abkuerzung_de,
                    fr=bod_master_attribution.abkuerzung_fr,
                    en=bod_master_attribution.abkuerzung_en,
                    it=bod_master_attribution.abkuerzung_it,
                    rm=bod_master_attribution.abkuerzung_rm,
                )

                attribution.save()

            # Create attribution for all orphaned datasets
            orphaned = Provider.objects.get(name="NO PROVIDER")
            ppbgdiattr, created = Attribution.objects.get_or_create(id=1000, provider=orphaned)

