from django.db import models
from django.db.models import Subquery, OuterRef
from django.utils.translation import gettext_lazy as _

from .managers import (
    TypeManager,
    DogmaAttributeManager,
    DogmaEffectManager,
    ItemCategoryManager,
    ItemGroupManager,
)


# TODO: Investigate effect of changing group_id to FK from integer field.


# Category Model
class ItemCategory(models.Model):
    category_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=250)
    published = models.BooleanField(default=True)

    objects = ItemCategoryManager()

    class Meta:
        default_permissions = ()


# Group Model
class ItemGroup(models.Model):
    group_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=250)
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    published = models.BooleanField(default=True)

    objects = ItemGroupManager()

    class Meta:
        default_permissions = ()


# Type Model
class Type(models.Model):
    type_name = models.CharField(max_length=500)
    type_id = models.BigIntegerField(primary_key=True)
    # group_id = models.IntegerField()    # This is essentially a FK field.
    group = models.ForeignKey(ItemGroup, on_delete=models.CASCADE, null=True)
    published = models.BooleanField(default=False)
    mass = models.FloatField(null=True)
    capacity = models.FloatField(null=True)
    description = models.CharField(
        max_length=5000, null=True
    )  # Not sure of the actual max.
    volume = models.FloatField(null=True)
    packaged_volume = models.FloatField(null=True)
    portion_size = models.IntegerField(null=True)
    radius = models.FloatField(null=True)
    graphic_id = models.IntegerField(null=True)
    icon_id = models.IntegerField(null=True)
    market_group_id = models.IntegerField(null=True)

    objects = TypeManager()

    class Meta:
        default_permissions = ()


# Dogma Attribute
class DogmaAttribute(models.Model):
    # 12 - Low Slots | 13 - Med Slots | 14 - High Slots
    # 1137 - Rig Slots | 1367 - Sub System Slots | 2056 - Service Slots
    # 182 | 183 | 184 --- Req Skill 1/2/3
    # 277 - Req. Skill 1 Lvl | 278 | 279 -- Req Skill 1/2 Lvl
    # 1374 - HiSlotModifier | 1375 - MedSlotModifier | 1376 - RigSlotModifier
    type = models.ForeignKey(
        Type, on_delete=models.DO_NOTHING, related_name="dogma_attributes"
    )
    attribute_id = models.IntegerField()
    value = models.FloatField()

    objects = DogmaAttributeManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=("attribute_id", "type"), name="unique_type_and_attribute_id"
            )
        ]


# Dogma Effect
class DogmaEffect(models.Model):
    # 11 - Low Power | 12 - High Power | 13 - Med Power
    # 2663 - Rig Slot | 3772 - Subsystem | 6306 - Service Slot
    type = models.ForeignKey(
        Type, on_delete=models.DO_NOTHING, related_name="dogma_effects"
    )
    effect_id = models.IntegerField()
    is_default = models.BooleanField()

    objects = DogmaEffectManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=("effect_id", "type"), name="unique_type_and_effect_id"
            )
        ]


# Fitting
class Fitting(models.Model):
    description = models.CharField(max_length=1000)  # unsure on max length here
    name = models.CharField(max_length=255, null=False)
    ship_type = models.ForeignKey(Type, on_delete=models.DO_NOTHING)
    ship_type_type_id = models.IntegerField()

    def __str__(self):
        return "{} ({})".format(self.ship_type.type_name, self.name)

    def eft(self):
        types = Type.objects.filter(type_id=OuterRef("type_id"))
        items = FittingItem.objects.filter(fit=self).annotate(
            item_name=Subquery(types.values("type_name"))
        )

        eft = "[" + self.ship_type.type_name + ", " + self.name + "]\n\n"

        temp = {"Cargo": [], "FighterBay": [], "DroneBay": []}

        slots = [
            {"key": "LoSlot", "range": 8},
            {"key": "MedSlot", "range": 8},
            {"key": "HiSlot", "range": 8},
            {"key": "RigSlot", "range": 3},
            {"key": "SubSystemSlot", "range": 4},
            {"key": "ServiceSlot", "range": 8},
        ]

        for item in items:
            if item.flag == "Cargo":
                temp["Cargo"].append(item)
            elif item.flag == "FighterBay":
                temp["FighterBay"].append(item)
            elif item.flag == "DroneBay":
                temp["DroneBay"].append(item)
            else:
                temp[item.flag] = item.item_name

        for slot in slots:
            isEmpty = True
            for i in range(0, slot["range"]):
                key = slot["key"] + str(i)
                if key in temp:
                    eft += temp[key] + "\n"
                    isEmpty = False
            if isEmpty == False:
                eft += "\n"

        slots = ["FighterBay", "DroneBay", "Cargo"]

        for slot in slots:
            if slot in temp:
                eft += "\n\n"
                for item in temp[slot]:
                    eft += item.item_name + " x" + str(item.quantity) + "\n"

        eft += "\n"

        return eft

    class Meta:
        default_permissions = ()
        permissions = (("access_fittings", "Can access the fittings module."),)
        unique_together = (("ship_type_type_id", "name"),)


# Fitting items
class FittingItem(models.Model):
    class Flag(models.TextChoices):
        CARGO = "Cargo", _("Cargo")
        DRONEBAY = "DroneBay", _("DroneBay")
        FIGHTERBAY = "FighterBay", _("FighterBay")
        HISLOT0 = "HiSlot0", _("HiSlot0")
        HISLOT1 = "HiSlot1", _("HiSlot1")
        HISLOT2 = "HiSlot2", _("HiSlot2")
        HISLOT3 = "HiSlot3", _("HiSlot3")
        HISLOT4 = "HiSlot4", _("HiSlot4")
        HISLOT5 = "HiSlot5", _("HiSlot5")
        HISLOT6 = "HiSlot6", _("HiSlot6")
        HISLOT7 = "HiSlot7", _("HiSlot7")
        INVALID = "Invalid", _("Invalid")
        LOSLOT0 = "LoSlot0", _("LoSlot0")
        LOSLOT1 = "LoSlot1", _("LoSlot1")
        LOSLOT2 = "LoSlot2", _("LoSlot2")
        LOSLOT3 = "LoSlot3", _("LoSlot3")
        LOSLOT4 = "LoSlot4", _("LoSlot4")
        LOSLOT5 = "LoSlot5", _("LoSlot5")
        LOSLOT6 = "LoSlot6", _("LoSlot6")
        LOSLOT7 = "LoSlot7", _("LoSlot7")
        MEDSLOT0 = "MedSlot0", _("MedSlot0")
        MEDSLOT1 = "MedSlot1", _("MedSlot1")
        MEDSLOT2 = "MedSlot2", _("MedSlot2")
        MEDSLOT3 = "MedSlot3", _("MedSlot3")
        MEDSLOT4 = "MedSlot4", _("MedSlot4")
        MEDSLOT5 = "MedSlot5", _("MedSlot5")
        MEDSLOT6 = "MedSlot6", _("MedSlot6")
        MEDSLOT7 = "MedSlot7", _("MedSlot7")
        RIGSLOT0 = "RigSlot0", _("RigSlot0")
        RIGSLOT1 = "RigSlot1", _("RigSlot1")
        RIGSLOT2 = "RigSlot2", _("RigSlot2")
        SERVICESLOT0 = "ServiceSlot0", _("ServiceSlot0")
        SERVICESLOT1 = "ServiceSlot1", _("ServiceSlot1")
        SERVICESLOT2 = "ServiceSlot2", _("ServiceSlot2")
        SERVICESLOT3 = "ServiceSlot3", _("ServiceSlot3")
        SERVICESLOT4 = "ServiceSlot4", _("ServiceSlot4")
        SERVICESLOT5 = "ServiceSlot5", _("ServiceSlot5")
        SERVICESLOT6 = "ServiceSlot6", _("ServiceSlot6")
        SERVICESLOT7 = "ServiceSlot7", _("ServiceSlot7")
        SUBSYSTEMSLOT0 = "SubSystemSlot0", _("SubSystemSlot0")
        SUBSYSTEMSLOT1 = "SubSystemSlot1", _("SubSystemSlot1")
        SUBSYSTEMSLOT2 = "SubSystemSlot2", _("SubSystemSlot2")
        SUBSYSTEMSLOT3 = "SubSystemSlot3", _("SubSystemSlot3")

    fit = models.ForeignKey(Fitting, on_delete=models.CASCADE, related_name="items")
    flag = models.CharField(max_length=25, choices=Flag.choices, default=Flag.INVALID)
    quantity = models.IntegerField(default=1)
    type_fk = models.ForeignKey(Type, on_delete=models.DO_NOTHING)
    type_id = models.IntegerField()

    class Meta:
        default_permissions = ()


# Doctrine
class Doctrine(models.Model):
    name = models.CharField(max_length=255, null=False)
    icon_url = models.URLField(null=True)
    fittings = models.ManyToManyField(Fitting, related_name="doctrines")
    description = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(null=True)

    class Meta:
        default_permissions = ()
        permissions = (("manage", "Can manage doctrines and fits."),)
