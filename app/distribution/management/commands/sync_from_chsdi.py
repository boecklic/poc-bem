import re
import os
import logging
import dateutil.parser
import subprocess
import ast
from pprint import pprint
import psycopg2
from multiprocessing import Pool
import json

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.utils.dateparse import parse_datetime
from django.utils import timezone

import mptt

from distribution.models import Dataset, FeatureCollection, VectorModel

logger = logging.getLogger('default')

ClassDefinitions = {}
Register = {}


class ClassDefinitionVisitor(ast.NodeVisitor):

    def __init__(self, db_name, *args, **kwargs):
        self.db_name = db_name
        super().__init__(*args, **kwargs)

    def visit_ClassDef(self, node):
        # Example:
        # --------------------------
        # ClassDef(
        #     name='AmtlichesStrassenverzeichnis',
        #     bases=[
        #         Name(id='Base', ctx=Load()),
        #         Name(id='Vector', ctx=Load())],
        #     keywords=[],
        #     body=[
        #         Assign(
        #             targets=[
        #                 Name(id='__tablename__', ctx=Store())],
        #             value=Constant(value='streetnames_tooltip')),
        #         Assign(
        #             targets=[
        #                 Name(id='__table_args__', ctx=Store())],
        #             value=Dict(
        #                 keys=[
        #                     Constant(value='schema'),
        #                     Constant(value='autoload')],
        #                 values=[
        #                     Constant(value='vd'),
        #                     Constant(value=False)])),

        if isinstance(node, ast.ClassDef):
            # print(f"Detected class Definition {node.name}")

            _cls = {}
            _cls['fields'] = {}
            _cls['fields']['__db_name__'] = self.db_name
            _cls['bases'] = []
            _cls['ast'] = node

            # check base classes
            for base in node.bases:
                # we don't care about Base and Vector
                # base classes for fields
                if base.id not in ['Base', 'Vector']:
                    _cls['bases'].append(base.id)
                    if base.id not in ClassDefinitions:
                        print(f'--WARN didn\'t find base class {base.id}')
                    else:
                        _cls['fields'] = ClassDefinitions[base.id]['fields']

            # check class fields
            # Example:
            # -------------------
            # body=[
            #     Assign(
            #         targets=[
            #             Name(id='__tablename__', ctx=Store())],
            #         value=Constant(value='fixpunkte_lfp2')),
            #     Assign(
            #         targets=[
            #             Name(id='__table_args__', ctx=Store())],
            #         value=Dict(
            #             keys=[
            #                 Constant(value='schema'),
            #                 Constant(value='autoload')],
            #             values=[
            #                 Constant(value='vd'),
            #                 Constant(value=False)])),

            # loop over all fields in the class definition
            # pattern is
            # id = Column('bgdi_id', Integer, primary_key=True)
            for field in node.body:
                print(ast.dump(field.value, indent=4))
                fieldvalue = {}
                if isinstance(field, ast.Assign):
                    # left side of assignment must be a single value (e.g. 'id'
                    # in the example above)
                    if len(field.targets) > 1:
                        print("--WARN I don't know how to handle targets with more than one entry")
                    else:
                        fieldname = field.targets[0].id

                    # e.g. __template__ = 'templates/htmlpopup/geomol_temperatur_top.mako'
                    if isinstance(field.value, ast.Constant):
                        fieldvalue = field.value.value
                    elif isinstance(field.value, ast.Dict):
                        keys = []
                        values = []
                        for key in field.value.keys:
                            if isinstance(key, ast.Constant):
                                keys.append(key.value)
                            else:
                                keys.append(None)
                        for val in field.value.values:
                            if isinstance(val, ast.Constant):
                                values.append(val.value)
                            else:
                                values.append(None)
                        fieldvalue = dict(map(lambda k, v: (k,v), keys, values))
                    elif isinstance(field.value, ast.Call):
                        primary_key = None
                        db_col_name = fieldname
                        if field.value.func.id == 'Column':
                            for arg in field.value.args:
                                if isinstance(arg, ast.Constant):
                                    db_col_name = arg.value
                                elif isinstance(arg, ast.Name):
                                    db_col_typ = arg.id
                            for keyword in field.value.keywords:
                                if keyword.arg == 'primary_key':
                                    primary_key = keyword.value.value
                            fieldvalue = {
                                'db_col_name': db_col_name,
                                'db_col_typ': db_col_typ
                            }
                            if primary_key:
                                fieldvalue['primary_key'] = primary_key
                        print(fieldname, fieldvalue)
                    else:
                        print(type(field.value), field.value)

                    _cls['fields'][fieldname] = fieldvalue

            ClassDefinitions[node.name] = _cls
        self.generic_visit(node)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call) and node.value.func.id == 'register':
            if len(node.value.args) != 2:
                print(f'--WARN register() is called with more or less than 2 args')
                print(ast.dump(node, indent=4))
            else:
                _id, _model = node.value.args
                if isinstance(_id, ast.Constant):
                    id = _id.value
                elif isinstance(_id, ast.Attribute):
                    # print(ast.dump(_id, indent=4))
                    fieldmodel = _id.value.id
                    field = _id.attr
                    if fieldmodel in ClassDefinitions and field in ClassDefinitions[fieldmodel]['fields']:
                        id = ClassDefinitions[fieldmodel]['fields'][field]
                    else:
                        pprint(ClassDefinitions.get(fieldmodel, {}))
                        print(f'--WARN couldn\'t find {field} field in model {fieldmodel}')
                model = _model.id
                Register[id] = model

        self.generic_visit(node)


def parse_python_file(file: str) -> ast.Module:
    with open(file, 'r') as f:
        tree = ast.parse(f.read())
    return tree


def get_table_schema(database, tablename, schema='public'):
    try:
        conn = psycopg2.connect(host='127.0.0.1', port=15432, database=database, user='www-data', password='www-data')
    except Exception as e:
        print(e)
        raise

    q = """
    SELECT column_name, data_type, character_octet_length, is_nullable
    FROM information_schema.columns
    WHERE table_name = %s;
    """

    cur = conn.cursor()
    cur.execute(q, (tablename,))  # (table_name,) passed as tuple
    result = cur.fetchall()
    print(result)
    return result

    # Example Output
    # [('column_a', 'integer', 'YES'),
    # ('column_b', 'boolean', 'NO'),
    # ...,
    # ]


def get_primary_key(database, tablename, schema='public'):
    try:
        conn = psycopg2.connect(host='127.0.0.1', port=15432, database=database, user='www-data', password='www-data')
    except Exception as e:
        print(e)
        raise
    q = """
    SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type
    FROM   pg_index i
    JOIN   pg_attribute a ON a.attrelid = i.indrelid
                        AND a.attnum = ANY(i.indkey)
    WHERE  i.indrelid = %s::regclass
    AND    i.indisprimary;
    """

    cur = conn.cursor()
    print(database,f'{schema}.{tablename}')
    cur.execute(q, (f'{schema}.{tablename}',))  # (table_name,) passed as tuple
    result = cur.fetchall()
    print(result)
    return result


class Command(BaseCommand):
    help = 'Syncs mfchsdi3 data with layers models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--featurecollections',
            action='store_true',
            help='Sync Feature Collections'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test function'
        )

    def handle(self, *args, **options):
        if options['test']:
            file = 'sources/mf-chsdi3/chsdi/models/vector/stopo.py'
            tree = parse_python_file(file)
            db_name = ""
            for node in tree.body:
                if isinstance(node, ast.Assign) and len(node.targets) == 1 and node.targets[0].id == 'Base':
                    db_name = node.value.slice.value
                    break
            visitor = ClassDefinitionVisitor(db_name=f'{db_name}_prod')
            visitor.visit(tree)
            with open('stopo.ast','w') as f:
                f.write(ast.dump(tree, indent=4))
            pprint(ClassDefinitions, indent=4)


        if options['featurecollections']:
            dbcluster_available = False
            try:
                conn = psycopg2.connect(host='127.0.0.1', port=15432, database='stopo_prod', user='www-data', password='www-data')
            except Exception as e:
                print(e)
            else:
                dbcluster_available = True

            # Find files that contain model definitions
            process = subprocess.Popen([f'grep -irnEl "^register\\(" sources/mf-chsdi3/*'],
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True)
            files, stderr = process.communicate()

            for file in files.strip().split('\n'):
                tree = parse_python_file(file)
                db_name = ""
                for node in tree.body:
                    if isinstance(node, ast.Assign) and len(node.targets) == 1 and node.targets[0].id == 'Base':
                        db_name = node.value.slice.value
                        break
                visitor = ClassDefinitionVisitor(db_name=f'{db_name}_master')
                visitor.visit(tree)

            with open('classdefinitions-dump.json','w') as f:
                pprint(ClassDefinitions, f)

            for dataset_id, modelname in Register.items():
                try:
                    dataset = Dataset.objects.get(name=dataset_id)
                except:
                    print(f"no dataset for {dataset_id}")
                    dataset = Dataset.objects.get(name="ORPHANED")

                if modelname not in ClassDefinitions:
                    print(f'--WARN {modelname} not found in ClassDefinitions')
                    continue
                model = ClassDefinitions[modelname]

                vector_model, created = VectorModel.objects.get_or_create(provider=dataset.provider, name=modelname)
                if dbcluster_available:
                    try:
                        table_schema = get_table_schema(model['fields']['__db_name__'], model['fields']['__tablename__'])
                        pk_field = get_primary_key(database=model['fields']['__db_name__'], tablename=model['fields']['__tablename__'], schema=model['fields'].get('__table_args__', {}).get("schema", "public"))
                    except Exception as e:
                        print(e)
                        pass
                    else:
                        vector_model.db_fields = {k:v for k,v,_,_ in table_schema}
                vector_model.chsdi_fields = model['fields']
                vector_model.save()


                featurecollection, created = FeatureCollection.objects.get_or_create(dataset=dataset,slug=modelname)
                featurecollection.used_in_feature_api = True
                featurecollection.db_table = model['fields']['__tablename__']
                featurecollection.db_schema = model['fields'].get('__table_args__', {}).get("schema", "public")
                featurecollection.db_name = model['fields']['__db_name__']

                if not featurecollection.mf_chsdi_models or modelname not in featurecollection.mf_chsdi_models:
                    if not featurecollection.mf_chsdi_models:
                        featurecollection.mf_chsdi_models = [modelname]
                    else:
                        featurecollection.mf_chsdi_models.append(modelname)

                featurecollection.mf_chsdi_file = file
                featurecollection.mf_chsdi_model_definitions = [ast.unparse(model['ast'])]

                featurecollection.save()
