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



def validate_not_none(value):
    if value == 'none':
        raise ValidationError(
            _('TranslationKey "%(value)s" is not valid'),
            params={'value': value},
        )



class TranslationKey(models.Model):

    id = models.SlugField(max_length=512, primary_key=True, validators=[validate_not_none])
    translation = models.OneToOneField(
        'translation.Translation',
        on_delete=models.SET_NULL,
        related_name='current_translation_key',
        null=True
    )

    def __str__(self):
        return self.id


class Translation(Versioned):

    translation_key = models.ForeignKey(
        'translation.TranslationKey',
        related_name='translation_versions',
        on_delete=models.CASCADE)
    de = models.TextField(null=True)
    fr = models.TextField(null=True)
    it = models.TextField(null=True)
    en = models.TextField(null=True)
    rm = models.TextField(null=True)


class TranslatableMixin(object):

    def create_or_update_translations(self, _id, de, fr, it, en, rm):

        validate_not_none(_id)
        translation_key, created = TranslationKey.objects.get_or_create(id=_id)

        translation = translation_key.translation or Translation(translation_key=translation_key)

        # check if sth changed at all, if not, don't create a new object
        if translation.de == de and \
            translation.fr == fr and \
            translation.it == it and \
            translation.en == en and \
            translation.rm == rm:
            # no changes
            pass    
        else:
            translation.de = de
            translation.fr = fr
            translation.it = it
            translation.en = en
            translation.rm = rm
        
            translation.save()

            
            logger.debug("created new translation for {} with key {}, revision {}".format(
                type(self),
                _id,
                translation.revision
            ))
        return translation_key
