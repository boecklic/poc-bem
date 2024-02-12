import os
import logging
import dateutil.parser
import subprocess
import requests
from lxml import html

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.utils.dateparse import parse_datetime
from django.utils import timezone

import mptt

from distribution.models import Dataset, DownloadCollection
from provider.models import Provider
from bod_master.models import BODDataset, BODContactorganisation
from translation.models import Translation, create_or_update_translations, generate_key



logger = logging.getLogger('default')


class Command(BaseCommand):
    help = 'Creates Example data in the new structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--html',
            action='store_true',
            help='Sync entries in html page'
        )
        parser.add_argument(
            '--stac',
            action='store_true',
            help='Sync collections from stac'
        )

    def handle(self, *args, **options):

        if options['html']:
            result = requests.get("https://data.geo.admin.ch")

            # Parse the document
            tree = html.fromstring(result.text)
            content = tree.xpath("//div[@id = 'data']")
            text_content = content[0].text_content().strip()
            # print(text_content)
            for entry in text_content.split('\n'):
                # comments in the html lead to empty lines, we skip those
                if not entry.strip():
                    continue
                # print(entry)
                values = entry.split(' ')
                try:
                    dataset = Dataset.objects.get(name=values[0])
                except:
                    print(f"--WARN no dataset found for {values[0]}")
                    continue

                downloadcollection, created = DownloadCollection.objects.get_or_create(dataset=dataset, slug=values[0])

        if options['stac']:
            nxt = "https://data.geo.admin.ch/api/stac/v0.9/collections"
            collections = []
            while nxt:
                result = requests.get(nxt)
                payload = result.json()
                if 'collections' in payload:
                    collections += payload['collections']

                nxt = None
                for link in payload['links']:
                    if link['rel'] == 'next':
                        nxt = link['href']

            print(f'nr collections: {len(collections)}')
            for collection in collections:
                try:
                    dataset = Dataset.objects.get(name=collection['id'])
                except:
                    print(f"--WARN no dataset for collection id {collection['id']}")
                    continue

                downloadcollection, created = DownloadCollection.objects.get_or_create(dataset=dataset, slug=collection['id'])
                downloadcollection.in_stac = True
                downloadcollection.save()

                if not 'providers' in collection:
                    print(f'--WARN collection {collection['id']} has no providers section')
                    continue

                if len(collection['providers']) > 0:
                    prov = collection['providers'][0]
                    try:
                        provider = Provider.objects.get(name=prov['name'])
                        if provider.name != dataset.provider.name:
                            print(f'--WARN provider in collection {prov['name']} is different from provider of dataset {dataset.provider.name}')
                    except:
                        print(f'--WARN provider {prov['name']} doesn\'t exist yet')
                else:
                    print(f'--WARN {collection['id']} doesn\'t have providers')

                if len(collection['providers']) > 1:
                    print(f'--WARN {collection['id']} has more than one provider, it has {len(collection['providers'])}')




