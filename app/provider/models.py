from django.db import models
from django.utils.translation import gettext as _


# Create your models here.

class Provider(models.Model):
    name = models.CharField(max_length=64)
    prefix = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Attribution(models.Model):
    provider = models.ForeignKey('provider.Provider', on_delete=models.CASCADE)
    name = models.OneToOneField(
        'translation.Translation',
        verbose_name=_('name'),
        on_delete=models.SET_NULL,
        related_name='attribution_name',
        null=True
    )
    short = models.OneToOneField(
        'translation.Translation',
        verbose_name=_('short'),
        on_delete=models.SET_NULL,
        related_name='attribution_short',
        null=True
    )

    def __str__(self):
        if not self.name:
            return ""
        else:
            return self.name.de
