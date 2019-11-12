from .models import Fitting, FittingItem, Type
from celery import shared_task


class EftParser:
    def __init__(self, eft_text):
        self.eft_lines = eft_text.strip().splitlines()

    def parse(self):
        modules = []
        cargo_drone = []
        ship_type = ''
        fit_name = ''
        counter = 0     # Slot flag number

        for line in self.eft_lines:
            if line == '':
                counter = 0
                continue

            if line.startswith('['):
                if ', ' in line:
                    ship_type, fit_name = line[1:-1].split(', ')

                if 'empty' in line.strip('[]').lower():
                    continue

            else:
                if ', ' in line:
                    module, charge = line.split(', ')
                    modules.append({'name': module, 'charge': charge, 'count': counter})
                else:
                    quantity = line.split()[-1]  # Quantity will always be the last element, if it is there.

                    if 'x' in quantity:
                        item_name = line.strip(quantity).strip()
                        cargo_drone.append({'name': item_name, 'quantity': int(quantity.strip('x'))})
                    else:
                        modules.append({'name': line.strip(), 'charge': '', 'count': counter})
            counter += 1

        return {'ship': ship_type, 'name': fit_name, 'modules': modules, 'cargo_drones': cargo_drone}


def _get_type(type_name):
    try:
        type_obj = Type.objects.get(name=type_name)
    except:
        type_obj = Type.objects.create_type(type_name)
    return type_obj


@shared_task()
def create_fitting_item(fit_pk, item):
    count = None
    quantity = None
    if 'count' in item:
        count = item['count']

    type_obj = _get_type(item['name'])

    # Dogma Effects
    flags = {11: 'LoSlot', 12: 'HiSlot', 13: 'MedSlot', 2663: 'RigSlot', 3772: 'SubSystemSlot', 6306: 'ServiceSlot'}
    effects = type_obj.dogma_effects.filter(effect_id__in=flags).values_list('effect_id', flat=True)
    if len(effects) == 0:
        flag = 'Cargo'
        quantity = item[quantity]
    elif count is None:
        flag = flags[effects[0]] + str(count)

    item = FittingItem.objects.create(flag=flag, quantity=None, type=type_obj, type_id=type_obj.pk, fit__pk=fit_pk)


@shared_task
def create_fit(eft_text, description=None):
    parsed_eft = EftParser(eft_text).parse()

    def __create_fit(ship_type, name, description):
        type_obj = _get_type(ship_type)
        fit = Fitting.objects.create(ship_type=type_obj, ship_type_id=type_obj.pk, name=name, description=description)
        return fit

    fit = __create_fit(parsed_eft['ship_type'], parsed_eft['name'], description)

    for module in parsed_eft['modules']:
        create_fitting_item(fit.pk, module)

    for item in parsed_eft['cargo_drones']:
        create_fitting_item(fit.pk, item)
