# Generated by Django 2.2 on 2019-08-20 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0016_mapservergroup_mapserver_group_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='mapserverlayer',
            name='wms_enable_request',
            field=models.CharField(default='*', max_length=128),
        ),
    ]
