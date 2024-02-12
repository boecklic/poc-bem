from django.db import models


class Layer(models.Model):
    style = models.ForeignKey('distribution.VectorStyle', on_delete=models.PROTECT)

    class Meta:
        abstract = True


class VectorLayer(models.Model):
    feature_collection = models.ForeignKey('distribution.FeatureCollection', on_delete=models.PROTECT)
