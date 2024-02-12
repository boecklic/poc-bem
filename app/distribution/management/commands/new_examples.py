import os
import logging
import dateutil.parser
import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.utils.dateparse import parse_datetime
from django.utils import timezone

import mptt

from distribution.models import Dataset, Attribution, FeatureCollection#, Metadata, Tileset
from provider.models import Provider
# from catalog.models import Topic, CatalogLayer, CatalogEntry
# from geo.models import SRS, srs_from_str
# from bod_master.models import Tileset as bod_master_Tileset
from bod_master.models import BODDataset, BODContactorganisation
# from bod_master.models import Topic as bod_master_Topic
# from bod_master.models import Catalog as bod_master_Catalog
# from bod_master.models import XTDatasetCatalog as bod_master_XTDatasetCatalog
# from bod_master.models import GeocatImport as bod_master_GeocatImport
from translation.models import Translation, create_or_update_translations, generate_key



logger = logging.getLogger('default')





class Command(BaseCommand):
    help = 'Creates Example data in the new structure'

    # def add_arguments(self, parser):
        # parser.add_argument(
        #     '--topics',
        #     action='store_true',
        #     help='Sync topics'
        # )

    def handle(self, *args, **options):

        provider, created = Provider.objects.get_or_create(name="newexample")
        attribution, created = Attribution.objects.get_or_create(id=1001, prefix="new.example", provider=provider)

        swissimage, created = Dataset.objects.get_or_create(
            name="ch.example.swissimage",
            provider=provider,
            attribution=attribution,
            abstract=create_or_update_translations(
                "example_abstract_ch.example.swissimage",
                de="SWISSIMAGE",
                fr="SWISSIMAGE",
                en="SWISSIMAGE",
                it="SWISSIMAGE",
                rm="SWISSIMAGE"
            ))
        swissimage.geocat_id = "db5a52b4-0f5f-4998-a9a8-dd9539f93808"
        swissimage.save()

        feat1, created = FeatureCollection.objects.get_or_create(
            dataset=swissimage,
            slug="ch.example.swissimage.product_metadata"
        )

        feat2, created = FeatureCollection.objects.get_or_create(
            dataset=swissimage,
            slug="ch.example.swissimage.dop10_metadata"
        )
