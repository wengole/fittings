from django.db import models
from esi.clients import esi_client_factory


class TypeManager(models.Manager):
    @staticmethod
    def __get_type_id(self, type_name):
        payload = [type_name]
        c = esi_client_factory()
        ids = c.Universe.post_universe_ids(names=payload).result()
        _id = ids.get("inventory_types")[0].get("id")
        return _id

    def create_type(self, type_name):
        _id = self.__get_type_id(self, type_name)
        c = esi_client_factory()
        type_result = c.Universe.get_universe_types_type_id(type_id=_id).result()
        type_name = type_result.pop('name')
        type_result['type_name'] = type_name
        attributes = type_result.pop('dogma_attributes')
        effects = type_result.pop('dogma_effects')
        group_result = c.Universe.get_universe_groups_group_id(group_id=type_result['group_id']).result()
        type_result.append({'category_id' : group_result['category_id']})


        obj = self.update_or_create(type_id=_id, defaults=type_result)

        # Handle Attributes
        from .models import DogmaAttribute
        DogmaAttribute.objects.bulk_attributes(attributes, obj[0].pk)

        # Handle Effects
        from .models import DogmaEffect
        DogmaEffect.objects.bulk_effects(effects, obj[0].pk)

        return obj[0]


class DogmaAttributeManager(models.Manager):
    def bulk_attributes(self, attributes, type_pk):
        for attribute in attributes:
            attribute['type_id'] = type_pk
            att = self.update_or_create(type_id=type_pk, attribute_id=attribute['attribute_id'], defaults=attribute)


class DogmaEffectManager(models.Manager):
    def bulk_effects(self, effects, type_pk):
        for effect in effects:
            effect['type_id'] = type_pk
            eff = self.update_or_create(type_id=type_pk, effect_id=effect['effect_id'], defaults=effect)
