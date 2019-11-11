from django.db import models
from model_utils import Choices


# Fitting
class Fitting(models.Model):
    description = models.CharField(max_length=1000)  # unsure on max length here
    fitting_id = models.IntegerField()
    name = models.CharField(max_length=255, null=False)
    ship_type_id = models.IntegerField()


# Fitting items
class FittingItem(models.Model):
    _flag_enum = Choices('Cargo', 'DroneBay', 'FighterBay', 'HiSlot0', 'HiSlot1', 'HiSlot2',
                         'HiSlot3', 'HiSlot4', 'HiSlot5', 'HiSlot6', 'HiSlot7', 'Invalid',
                         'LoSlot0', 'LoSlot1', 'LoSlot2', 'LoSlot3', 'LoSlot4', 'LoSlot5',
                         'LoSlot6', 'LoSlot7', 'MedSlot0', 'MedSlot1', 'MedSlot2', 'MedSlot3',
                         'MedSlot4', 'MedSlot5', 'MedSlot6', 'MedSlot7', 'RigSlot0', 'RigSlot1',
                         'RigSlot2', 'ServiceSlot0', 'ServiceSlot1', 'ServiceSlot2', 'ServiceSlot3',
                         'ServiceSlot4', 'ServiceSlot5', 'ServiceSlot6', 'ServiceSlot7', 'SubSystemSlot0',
                         'SubSystemSlot1', 'SubSystemSlot2', 'SubSystemSlot3')
    flag = models.CharField(max_length=25, choices=_flag_enum, default='Invalid')
    quantity = models.IntegerField()
    type_id = models.IntegerField()


# Doctrine
class Doctrine(models.Model):
    name = models.CharField(max_length=255, null=False)
    icon_url = models.URLField(null=True)
    fittings = models.ManyToManyField(Fitting, related_name='doctrines')
    description = models.CharField(max_length=1000)


# Dogma Attribute
class DogmaAttribute(models.Model):
    # 12 - Low Slots | 13 - Med Slots | 14 - High Slots
    # 1137 - Rig Slots | 1367 - Sub System Slots | 2056 - Service Slots
    # 182 | 183 | 184 --- Req Skill 1/2/3
    # 277 - Req. Skill 1 Lvl | 278 | 279 -- Req Skill 1/2 Lvl
    attribute_id = models.IntegerField()
    value = models.DecimalField()


# Dogma Effect
class DogmaEffect(models.Model):
    # 11 - Low Power | 12 - High Power | 13 - Med Power
    # 2663 - Rig Slot | 3772 - Subsystem | 6306 - Service Slot
    effect_id = models.IntegerField()
    is_default = models.BooleanField()


# Type Model
class Type(models.Model):
    name = models.CharField(max_length=500)
    type_id = models.BigIntegerField(primary_key=True)
    group_id = models.IntegerField()
    published = models.BooleanField(default=False)
    dogma_attributes = models.ManyToManyField(DogmaAttribute, related_name='types')
    dogma_effects = models.ManyToManyField(DogmaEffect, related_name='types')
    mass = models.FloatField(null=True)
    capacity = models.FloatField(null=True)
    description = models.CharField(max_length=5000, null=False)  # Not sure of the actual max.
    volume = models.FloatField(null=True)
    packaged_volume = models.FloatField(null=True)
    portion_size = models.IntegerField(null=True)
    radius = models.FloatField(null=True)
