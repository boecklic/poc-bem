from django.db import models

# Create your models here.

class Publisher(models.Model):
    name = models.CharField(max_length=64)
    STAGING_CHOICE_DEV = 'dev'
    STAGING_CHOICE_INT = 'int'
    STAGING_CHOICE_PROD = 'prod'
    STAGING_CHOICES = (
        (STAGING_CHOICE_DEV, 'development'),
        (STAGING_CHOICE_INT, 'integration'),
        (STAGING_CHOICE_PROD, 'production')
    )
    staging = models.CharField(max_length=16, choices=STAGING_CHOICES, default=STAGING_CHOICE_DEV)
    fqdn = models.CharField(max_length=256, default='bgdi.ch')

    class Meta:
        abstract = True


    def __str__(self):
        return self.name

class WMTS(Publisher):
    pass


class WMS(Publisher):
    pass


class GeoJSON(Publisher):
    pass