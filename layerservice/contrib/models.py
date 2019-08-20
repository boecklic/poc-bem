import logging

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger('default')

# Create your models here.

class VersionedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(current=True)


class Versioned(models.Model):

    current = models.BooleanField(default=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    revision = models.PositiveIntegerField(default=0)
    # created_by = models.ForeignKey('user.User')

    objects = models.Manager()
    currents = VersionedManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # set id to None to force creation of a new
        # object
        self.id = None
        self.revision += 1

        # set 'current' for all objects with the
        # same translation_key to False
        cls = type(self)
        cls.objects.filter(translation_key_id=self.translation_key_id)\
            .update(current=False)
        super().save(*args, **kwargs)

        # update the TranslationKey object to point
        # to self
        self.translation_key.translation = self
        self.translation_key.save()


