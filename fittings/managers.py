from django.db import models
from esi.clients import esi_client_factory
import pysnooper


class TypeManager(models.Manager):
    @staticmethod
    def __get_type_id(self, type_name):
        payload = [type_name]
        c = esi_client_factory()
        ids = c.Universe.post_universe_ids(names=payload).result()
        _id = ids.get("inventory_types")[0].get("id")
        return _id

    def create_type(self, type_name):
        _id = self.__get_type_id(type_name)
        c = esi_client_factory()
        type_result = c.Universe.get_universe_types_type_id(type_id=_id).result()
        attributes = type_result.pop('dogma_attributes')
        effects = type_result.pop('dogma_effects')

        obj = self.create(**type_result)

        # Handle Attributes
        from .models import DogmaAttribute
        DogmaAttribute.objects.bulk_attributes(attributes, obj.pk)

        # Handle Effects
        from .models import DogmaEffect
        DogmaEffect.objects.bulk_effects(effects, obj.pk)

        return obj


class DogmaAttributeManager(models.Manager):
    def bulk_attributes(self, attributes, type_pk):
        from .models import Type
        through_model = Type.dogma_attributes.through

        tms = []
        for attribute in attributes:
            print(attribute)
            att = self.create(**attribute)
            tm = through_model(type_id=type_pk, dogmaattribute_id=att.pk)
            tms.append(tm)

        through_model.objects.bulk_create(tms)


class DogmaEffectManager(models.Manager):
    def bulk_effects(self, effects, type_pk):
        from .models import Type
        through_model = Type.dogma_effects.through

        tms = []
        for effect in effects:
            eff = self.create(**effect)
            tm = through_model(type_id=type_pk, dogmaeffect_id=eff.pk)
            tms.append(tm)

        through_model.objects.bulk_create(tms)