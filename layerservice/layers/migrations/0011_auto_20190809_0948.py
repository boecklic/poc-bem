# Generated by Django 2.2 on 2019-08-09 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0010_auto_20190809_0911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='abstract_key',
            field=models.SlugField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='description_key',
            field=models.SlugField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='short_description_key',
            field=models.SlugField(max_length=500, null=True),
        ),
    ]
