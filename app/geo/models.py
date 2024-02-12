import re

from django.db import models

# Create your models here.

SUPPORTED_SRS = [
2056,
21781,
4326,
3857
]

srsre = re.compile(r'(?P<epsg>{})'.format('|'.join(str(srs) for srs in SUPPORTED_SRS)))

def srs_from_str(s):
    try:
        srs = srsre.search(s).groupdict()['epsg']
    except Exception as e:
        print(e)
        raise ValueError('none of {} could be found in {}'.format(','.join(str(srs) for srs in SUPPORTED_SRS), s))

    return srs


class SRS(models.Model):

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=512, null=True)

    @property
    def epsg(self):
        return "epsg:{}".format(self.id)
    
    def __str__(self):
        return "{} ({})".format(self.id, self.name)
