# Generated by Django 2.2 on 2019-08-09 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translation', '0004_auto_20190809_0911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translation',
            name='key',
            field=models.SlugField(max_length=500),
        ),
    ]
