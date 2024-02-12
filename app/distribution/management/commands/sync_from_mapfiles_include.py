import dateutil.parser
import mappyfile
import logging
import glob
import os
from pathlib import Path
import pprint
from multiprocessing import Process, Pool
import json
import re
import sys
import io
from sqlglot import exp, parse_one
from lark import Lark, Token

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.utils.dateparse import parse_datetime
from django.utils import timezone

import mptt

from distribution.models import Dataset, FeatureCollection, RasterCollection#, MapServerLayer, MapServerGroup
from translation.models import increment_suffix
# from geo.models import SRS, srs_from_str

logger = logging.getLogger('default')

mapfile_data = {}

report = io.StringIO()
i = ' '

def check_dataset(mapfile):

    # check first if we have a matching dataset
    dataset_name = Path(mapfile).stem
    try:
        dataset = Dataset.objects.get(name=dataset_name)
    except:
        print('--WARN  no matching dataset found for {}'.format(dataset_name))
        return mapfile, None

    # print('parsing {} (dataset_name {})'.format(mapfile, dataset_name))
    return mapfile, parse_mapfile(mapfile)


def parse_mapfile(mapfile):
    mjsn = []
    with open(mapfile, 'r') as f:
        # https://mappyfile.readthedocs.io/en/latest/api/main.html#mappyfile.loads
        # ignore includes for the moment
        cont = f.read()
        if 'INCLUDE' in cont:
            return None
        try:
            mjsn = mappyfile.loads(cont)#, expand_includes=False)
        except Exception as e:
            print(f"--WARN  couldn't parse mapfile for {mapfile}")
            print(e)

    # if mapfile contains just one layer, the parsing
    # result is not of type list
    if not isinstance(mjsn, list):
        mjsn = [mjsn]

    return mjsn

def get_dataset(dataset_name):
    try:
        dataset = Dataset.objects.get(name=dataset_name)
    except:
        print('--WARN  no matching dataset found for {}'.format(dataset_name))
        return None
    return dataset


def analyze_map_layer(args):
    mapfile = args[0]
    parsed = args[1]
    report = io.StringIO()
    print(mapfile, file=report)
    if not parsed:
        print(f"{i:2}not parsed", file=report)
        return report.getvalue()
    for layer in parsed:
        if "connectiontype" in layer and layer["connectiontype"] == "POSTGIS":
            dataset_name = Path(mapfile).stem
            print(f'{i:2}{layer['name']}', file=report)
            if 'group' in layer:
                if layer['group'] != dataset_name:
                    print(f'{i:4}--WARN groupname {layer['group']} different from dataset name {dataset_name}', file=report)
                    return report.getvalue()

            dataset = get_dataset(dataset_name)
            if not dataset:
                return report.getvalue()

            featurecollection,created = FeatureCollection.objects.get_or_create(dataset=dataset, slug=layer['name'])
            featurecollection.used_in_wms_layer = True
            featurecollection.mapfile_data_string = layer['data']

            # parse dbname
            dbname = re.match(r'.*dbname=([^ ]*).*', layer['connection'])
            if dbname:
                featurecollection.db_name= dbname.group(1)
            else:
                print(f'{i:4}--WARN no dbname found in connection {layer['connection']}', file=report)

            print(f'{i:4}DATA:           {layer['data']}', file=report)
            try:
                tree = parser.parse(layer['data'].replace('\n', ' '))
            except Exception as e:
                print(f'{i:6}--ERR parsing failed:\n{i:6}{layer['data']}', file=report)
                print(f'{i:6}{e}', file=report)
            else:

                for match in tree.find_data(Token('RULE', 'geom_field')):
                    geom_field = match.children[0].value
                for match in tree.find_data(Token('RULE', 'sql_subquery')):
                    sql_subquery = match.children[0].value
                    sql_subquery = re.sub(' {2,}', ' ', sql_subquery.replace('%lang%', 'de'))
                    if 'scaletokens' in layer:
                        print(f'{i:6}SCALETOKENS:  {layer['scaletokens']}', file=report)
                        for scaletoken in layer['scaletokens']:
                            if scaletoken['name'] in sql_subquery:
                                # for the moment just replace the scaletoken with the first value
                                sql_subquery = sql_subquery.replace(scaletoken['name'], next(iter(scaletoken['values'].values())))
                    print(f'{i:6}SQL_SUBQUERY: {sql_subquery}', file=report)

                    try:
                        parsed_sql = parse_one(sql_subquery)
                    except:
                        print(f'{i:8}--ERR parsing of sql subquery failed', file=report)
                    else:
                        for table in parsed_sql.find_all(exp.Table):
                            print(f'{i:8}TABLE:      {table}', file=report)
                            splitted = str(table).split('.')
                            if len(splitted) == 2:
                                featurecollection.db_schema = splitted[0]
                                featurecollection.db_table = splitted[1]
                            elif len(splitted) == 1:
                                featurecollection.db_table = splitted[0]


            try:
                featurecollection.save()
            except Exception as e:
                print(report.getvalue())
                raise
    return report.getvalue()


parser = Lark("""
    # mapfiledata: "DATA"i DOUBLE_QUOTE statement DOUBLE_QUOTE

    statement: geom_field "FROM"i (table | sql_subquery) using*
    table: STRING_UNDERLINE? "."? STRING_UNDERLINE
    sql_subquery: SELECT_STRING "AS"i WORD

    geom_field: STRING_UNDERLINE
    using: using_unique
        | using_srid
    using_unique: "using unique"i WORD_UNDERLINE
    using_srid: "using srid="i SIGNED_NUMBER

    WORD_UNDERLINE: /[a-z_]+/
    STRING_UNDERLINE: /[a-z0-9_]+/
    SELECT_STRING: /\\(.+\\)/
    DATA: "DATA"i
    #  note: in a .lark file this would only need one backslash
    DOUBLE_QUOTE: "\\""


    %import common.WORD   // imports from terminal library
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING
    %ignore " "           // Disregard spaces in text
""", start='statement', ambiguity='explicit')


class Command(BaseCommand):
    help = 'Syncs mapfiles in mapfiles_include MapServerLayer models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--parse',
            action='store_true',
            help='Parse mapfiles and save as json'
        )
        parser.add_argument(
            '--rastercollections',
            action='store_true',
            help='Parse mapfiles and save as json'
        )
        parser.add_argument(
            '--featurecollections',
            action='store_true',
            help='Parse mapfiles and save as json'
        )
        parser.add_argument(
            '--parse-data-statement',
            action='store_true',
            help="Parse only DATA \"\" statements from mapfiles"
        )

    def handle(self, *args, **options):
        mapfiles_path = "sources/wms-mapfile_include"
        if options['parse_data_statement']:
            # The form of DATA is “[geometry_column] from [table_name|sql_subquery] using unique [unique_key] using srid=[spatial_reference_id]”



            with open('mapfiledata_statements.txt', 'r') as f:
                sentences = f.read()

            for sentence in sentences.split('\n')[0:2]:
                sentence = sentence.strip()

                if not sentence:
                    continue
                try:
                    ast = parser.parse(sentence)
                except Exception as e:

                    print(f'--WARN couldn\' parse mapfile data statement')
                    print(sentence)
                    print(e)
                else:
                    print(ast)
                    for match in ast.find_data(Token('RULE', 'geom_field')):
                        print(match)
                        geom_field = match.children[0].value
                    for match in ast.find_data(Token('RULE', 'sql_subquery')):
                        sql_subquery = match.children[0].value
                    print(geom_field, sql_subquery)
                    # pass
            # sentence = 'DATA "the_geom FROM blabla"'
            # print(sentence)
            # print(parser.parse(sentence).pretty())
            # sentence = 'DATA "the_geom FROM (SELECT as,df FROM table) as foo using unique blabla using srid=1234"'
            # print(sentence)
            # print(parser.parse(sentence).pretty())



        if options['parse']:

            mapfiles = glob.glob(f'{mapfiles_path}/*.map')
            print('starting to parse {} *.map files in dir {}'.format(len(mapfiles), mapfiles_path))
            mapfile_data = {}

            with Pool(16) as p:
                results = p.map(check_dataset, mapfiles)

            mapfile_data = dict((key, val) for key,val in results)
            print(f"parsed {len(mapfile_data)} mapfiles")

            with open("parse_mapfiles.json",'w') as f:
                json.dump(mapfile_data, f, indent=4)

        if options['rastercollections']:
            try:
                with open("parse_mapfiles.json", 'r') as f:
                    mapfile_data = json.loads(f.read())
            except:
                print("couldn't load preparsed mapfiles. run with --parse first")
                return

            for mapfile, parsed in mapfile_data.items():
                if not parsed:
                    continue
                for layer in parsed:
                    if layer["type"].lower() == "raster":
                        dataset_name = Path(mapfile).stem
                        dataset = get_dataset(dataset_name)
                        if not dataset:
                            continue
                        tiled = False
                        if 'data' in layer:
                            datafield = layer['data']
                        elif 'tileindex' in layer:
                            datafield = layer['tileindex']
                            tiled = True
                        else:
                            print(f'--WARN no data/tileindex entry found for layer {layer['name']} in mapfile {mapfile}')
                            continue
                            # pprint.pprint(layer)
                        if datafield.startswith('%'):
                            print(f"{layer['name']} DATA/TILEINDEX starting with scaletoken")
                            for scaletoken in layer['scaletokens']:
                                if scaletoken['name'] != datafield:
                                    continue
                                for value, file in scaletoken['values'].items():
                                    if value == '__type__':
                                        continue
                                    slug = layer['name']
                                    while RasterCollection.objects.filter(dataset=dataset, slug=slug).exists():
                                        slug = increment_suffix(slug)

                                    rastercollection,created = RasterCollection.objects.get_or_create(dataset=dataset, slug=slug)
                                    rastercollection.file = file
                                    rastercollection.tiled = tiled
                                    rastercollection.save()

                        else:
                            rastercollection,created = RasterCollection.objects.get_or_create(dataset=dataset, slug=layer['name'])
                            rastercollection.file = datafield
                            rastercollection.tiled = tiled
                            rastercollection.save()

        if options['featurecollections']:
            try:
                with open("parse_mapfiles.json", 'r') as f:
                    mapfile_data = json.loads(f.read())
            except:
                print("couldn't load preparsed mapfiles. run with --parse first")
                return

            with Pool(16) as p:
                results = p.map(analyze_map_layer, list(mapfile_data.items()))
            # print(results)

            with open("report_mapfiles.txt", 'w') as f:
                f.write('\n'.join(results))
