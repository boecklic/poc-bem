# Generated by Django 2.2 on 2019-08-09 09:11

from django.db import migrations, models
import django.db.models.manager
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0010_auto_20190809_0911'),
        ('catalog', '0007_auto_20190809_0911'),
        ('translation', '0003_auto_20190624_1418'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='translation',
            managers=[
                ('versioned', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='translation',
            name='key',
            field=models.SlugField(default=uuid.uuid4),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='translation',
            name='revision',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AlterUniqueTogether(
            name='translation',
            unique_together={('key', 'revision')},
        ),
        migrations.AlterIndexTogether(
            name='translation',
            index_together={('current', 'key')},
        ),
        migrations.RemoveField(
            model_name='translation',
            name='translation_key',
        ),
        migrations.DeleteModel(
            name='TranslationKey',
        ),
    ]
