from django.db import models


class RelatedOfRelatedModel(models.Model):
    rr_c1 = models.CharField(max_length=16)
    rr_f1 = models.IntegerField(null=True)
    rr_f2 = models.FloatField(null=True)
    rr_f3 = models.FloatField(null=True)


class RelatedModel(models.Model):
    r_c1 = models.CharField(max_length=16)
    r_f1 = models.IntegerField(null=True)
    r_f2 = models.FloatField(null=True)
    r_f3 = models.FloatField(null=True)
    r_related = models.ForeignKey(RelatedOfRelatedModel, on_delete=models.CASCADE)


class MainModel(models.Model):
    c1 = models.CharField(max_length=16)
    f1 = models.IntegerField(null=True)
    f2 = models.FloatField(null=True)
    f3 = models.FloatField(null=True)

    related = models.ForeignKey(RelatedModel, on_delete=models.CASCADE)

