from django.db import models
from django.utils.translation import gettext as _

from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.


class Topic(models.Model):

    name = models.CharField(max_length=64, unique=True)
    title_key = models.SlugField(null=True)
    # title = models.OneToOneField(
    #     'translation.Translation',
    #     verbose_name=_('title'),
    #     on_delete=models.SET_NULL,
    #     related_name='catalog_topic_title',
    #     to_field='key',
    #     null=True
    # )
    STAGING_CHOICE_TEST = 'test'
    STAGING_CHOICE_PROD = 'prod'
    STAGING_CHOICES = (
        (STAGING_CHOICE_TEST, 'testing environments (dev and int)'),
        (STAGING_CHOICE_PROD, 'production environment')
    )
    staging = models.CharField(
        max_length=16,
        choices=STAGING_CHOICES,
        default=STAGING_CHOICE_TEST
    )

    def __str__(self):
        return self.name


class CatalogEntry(MPTTModel):

    bodm_legacy_catalog_id = models.IntegerField()
    parent = TreeForeignKey('self', 
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True
    )
    datasets = models.ManyToManyField(
        'layers.Dataset',
        through='catalog.CatalogLayer'
    )
    topic = models.ForeignKey('catalog.Topic', on_delete=models.CASCADE)

    # name = models.ForeignKey(
    #     'translation.Translation',
    #     on_delete=models.SET_NULL,
    #     null=True)
    name = models.ForeignKey(
        'translation.Translation',
        verbose_name=_('name'),
        on_delete=models.SET_NULL,
        related_name='catalog_cataloglayer_name',
        null=True
    )

    def __str__(self):
        return self.name.key if self.name else '-'

class CatalogLayer(models.Model):
    catalog_entry = models.ForeignKey('catalog.CatalogEntry', on_delete=models.CASCADE)
    dataset = models.ForeignKey('layers.Dataset', on_delete=models.CASCADE)
    activated = models.BooleanField(default=False)

    class Meta:
        unique_together = (('catalog_entry', 'dataset'),)