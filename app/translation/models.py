import logging

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

logger = logging.getLogger('default')

# Create your models here.

TRANSLATION_KEY_MAX_LENGTH = 50


class VersionedManager(models.Manager):
    # Setting use_for_related_fields to True on the manager will make it
    # available on all relations that point to the model on which you defined
    # this manager as the default manager.
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().filter(current=True)


class Versioned(models.Model):

    current = models.BooleanField(default=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    key = models.SlugField(db_index=True, max_length=500)
    revision = models.PositiveIntegerField(default=0,db_index=True)
    # created_by = models.ForeignKey('user.User')

    # Note: The first manager defined is the default,
    # no matter how it's named
    versioned = VersionedManager()
    objects = models.Manager()

    class Meta:
        abstract = True
        unique_together = ('key', 'revision')
        index_together = (('current', 'key'),)

    def save(self, *args, **kwargs):
        # set id to None to force creation of a new
        # object
        self.id = None
        self.revision += 1

        # set 'current' for all objects with the
        # same key to False
        cls = type(self)
        cls.objects.filter(key=self.key)\
            .update(current=False)
        super().save(*args, **kwargs)

        # # update the TranslationKey object to point
        # # to self
        # self.translation_key.translation = self
        # self.translation_key.save()



def validate_not_none(value):
    if value == 'none':
        raise ValidationError(
            _('TranslationKey "%(value)s" is not valid'),
            params={'value': value},
        )



# class TranslationKey(models.Model):

#     id = models.SlugField(max_length=512, primary_key=True, validators=[validate_not_none])
#     translation = models.OneToOneField(
#         'translation.Translation',
#         on_delete=models.SET_NULL,
#         related_name='current_translation_key',
#         null=True
#     )

#     def __str__(self):
#         return self.id


class Translation(Versioned):

    de = models.TextField(null=True)
    fr = models.TextField(null=True)
    it = models.TextField(null=True)
    en = models.TextField(null=True)
    rm = models.TextField(null=True)

    def __str__(self):
        return f"{self.de}"

    def full_translation_list(self):
        return f"DE: {self.de} <br>FR: {self.fr} <br>IT: {self.it} <br>EN: {self.en} <br>RM: {self.rm}"

def create_or_update_translations(key, de, fr, it, en, rm):

    validate_not_none(key)

    translation, created = Translation.versioned.get_or_create(key=key)

    # translation = translation_key.translation or Translation(translation_key=translation_key)

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


        logger.debug("created new translation with key {}, revision {}".format(
            key,
            translation.revision
        ))
    return translation

def increment_suffix(s, separator='_'):
    parts = s.split(separator)
    try:
        suffix = int(parts[-1])
    except ValueError:
        # last part of the string is not an int
        suffix = "{}_1".format(parts[-1])
    else:
        suffix += 1
    parts[-1] = str(suffix)
    return separator.join(parts)



def generate_key(translation_object, key_proposal, prefix=""):
    if not translation_object:
        key = prefix + slugify(key_proposal[:TRANSLATION_KEY_MAX_LENGTH])
        while(Translation.versioned.filter(key=key).exists()):
            key = increment_suffix(key)
    else:
        key = translation_object.key

    return key
