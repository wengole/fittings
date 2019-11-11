from django.db import models


# Fitting
class Fitting(models.Model):
    description = models.CharField(max_length=1000)  # unsure on max length here
    fitting_id = models.IntegerField()
    name = models.CharField(max_length=255, null=False)
    ship_type_id = models.IntegerField()


# Fitting items
class FittingItem(models.Model):
    flag = models.IntegerField()
    quantity = models.IntegerField()
    type_id = models.IntegerField()


# Doctrine
class Doctrine(models.Model):
    name = models.CharField(max_length=255, null=False)
    icon_url = models.URLField(null=True)
    fittings = models.ManyToManyField(Fitting, related_name='doctrines')
    description = models.CharField(max_length=1000)


# Dogma
class Dogma(models.Model):
    # 12 - Low Slots | 13 - Med Slots | 14 - High Slots
    attribute_id = models.IntegerField()
    type_id = models.IntegerField()
    value = models.DecimalField()