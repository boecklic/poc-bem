# Generated by Django 2.2 on 2019-08-19 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0015_auto_20190819_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='mapservergroup',
            name='mapserver_group_name',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]