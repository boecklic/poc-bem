import dateutil.parser
import mappyfile
import logging
import glob
import os
from pathlib import Path
import pprint

import sys

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.utils.dateparse import parse_datetime
from django.utils import timezone

import mptt

from layers.models import Dataset, MapServerLayer, MapServerGroup
from geo.models import SRS, srs_from_str



logger = logging.getLogger('default')


class Command(BaseCommand):
    help = 'Syncs mapfiles in mapfiles_include MapServerLayer models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mapfiles_include',
            action='store',
            default='../../wms-mapfile_include/',
            help='Sync mapfiles'
        )


    def handle(self, *args, **options):
        mapfiles_include = options['mapfiles_include']
        curdir = os.getcwd()
        os.chdir(os.path.join(curdir,mapfiles_include))


        # remove trainling slash if present
        if mapfiles_include[-1] == '/':
            mapfiles_include = mapfiles_include[:-1]

        mapfiles = glob.glob('*.map')
        print('starting to parser {} *.map files in dir {}'.format(len(mapfiles), options['mapfiles_include']))

        for mapfile in mapfiles:
            mjsn = {}
            group = False
            
            try:
                # check first if we have a matching dataset
                dataset_name = Path(mapfile).stem
                try:
                    dataset = Dataset.objects.get(name=dataset_name)
                except:
                    print('  no matching dataset found for {}'.format(dataset_name))
                    continue

                print('parsing {} (dataset_name {})'.format(mapfile, dataset_name))
                
                with open(mapfile, 'r') as f:
                    # https://mappyfile.readthedocs.io/en/latest/api/main.html#mappyfile.loads
                    # ignore includes for the moment
                    cont = f.read()
                    if 'INCLUDE' in cont:
                        continue
                    mjsn = mappyfile.loads(cont)#, expand_includes=False)

                # pprint.pprint(mjsn)
                # if mapfile contains just one layer, the parsing
                # result is not of type list
                if not isinstance(mjsn, list):
                    mjsn = [mjsn]

                print('  {} contains {} layer(s)'.format(mapfile, len(mjsn)))

                for layer in mjsn:
                    # print('  layer {}'.format(layer))
                    # check if the layer belongs to a group
                    if 'group' in mjsn:
                        group = True
                        # Only set the group name if different from the layername
                        if layer['group'] != dataset_name:
                            mapserver_group_name = layer['group']
                        else:
                            mapserver_group_name = None
                        mapserver_layer_name = layer['name']
                    else:
                        mapserver_group_name = None
                        if layer['name'] != dataset_name:
                            mapserver_layer_name = layer['name']
                        else:
                            mapserver_layer_name = None
                    

                    print('  {}: {}, {}'.format(dataset_name, mapserver_group_name, mapserver_layer_name))
                    

                    mapservergroup, created = MapServerGroup.objects.get_or_create(
                        dataset=dataset,
                        mapserver_group_name=mapserver_group_name
                    )

                    mapserverlayer, created = MapServerLayer.objects.get_or_create(
                        group=mapservergroup,
                        mapserver_layer_name=mapserver_layer_name,
                        defaults={
                            'mapfile_json': layer
                        }
                    )
                    # default for status is on (in case missing in mapfile)
                    # sanitize cases like:
                    # 'status': DefaultOrderedDict(None, CaseInsensitiveOrderedDict())}]
                    layer['status'] = str(layer.get('status', 'on'))
                    mapserverlayer.status = layer['status'].lower() == 'on'

                    # sanitize cases like (token missing)
                    # 'units': DefaultOrderedDict(None, CaseInsensitiveOrderedDict())}]
                    layer['units'] = str(layer.get('units', 'meters'))
                    mapserverlayer.units = layer['units']
                    
                    try:
                        mapserverlayer.wms_extent = [int(x) for x in layer['metadata']['wms_extent'].split(' ')]
                    except:
                        pass
                    mapserverlayer.wms_enable_request = layer['metadata']['wms_enable_request']
                    mapserverlayer.mapfile = mappyfile.dumps(layer, indent=4, spacer=' ')
                    mapserverlayer.save()

            except Exception as e:
                print(repr(e))
                pprint.pprint(mjsn)
                # raise

        os.chdir(curdir)