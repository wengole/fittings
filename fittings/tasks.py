import os
import requests
import bz2
import sqlite3
import re

from .models import Fitting, FittingItem, Type, DogmaEffect, DogmaAttribute
from esi.clients import esi_client_factory
from celery import shared_task


class EftParser:
    def __init__(self, eft_text):
        self.eft_lines = eft_text.strip().splitlines()

    def parse(self):
        modules = []
        cargo_drone = []
        ship_type = ''
        fit_name = ''
        counter = 0  # Slot flag number
        last_line = ''
        end_fit = False

        for line in self.eft_lines:
            if last_line == '' and line == '':
                end_fit = True

            last_line = line
            if line == '':
                counter = 0
                continue

            if line.startswith('['):
                if ', ' in line:
                    ship_type, fit_name = line[1:-1].split(', ')
                    continue

                if 'empty' in line.strip('[]').lower():
                    continue

            else:
                if ',' in line:
                    module, charge = line.split(',')
                    modules.append({'name': module, 'charge': charge.strip(), 'count': counter})
                else:
                    quantity = line.split()[-1]  # Quantity will always be the last element, if it is there.

                    if 'x' in quantity and quantity[1:].isdigit():
                        item_name = line.strip(quantity).strip()
                        cargo_drone.append({'name': item_name, 'quantity': int(quantity.strip('x'))})
                    elif end_fit is True:
                        cargo_drone.append({'name': line.strip(), 'quantity': 1})
                    else:
                        modules.append({'name': line.strip(), 'charge': '', 'count': counter})
            counter += 1

        return {'ship': ship_type, 'name': fit_name, 'modules': modules, 'cargo_drones': cargo_drone}


class SDEConn:
    def __init__(self):
        self.conn = sqlite3.connect('sde.db', detect_types=sqlite3.PARSE_COLNAMES)
        self.cursor = self.conn.cursor()
        self.col_names = None

    first_cap_re = re.compile('(.)([A-Z][a-z]+)')
    all_cap_re = re.compile('([a-z0-9])([A-Z])')

    def __snake_case_from_camel(self, name):
        s1 = self.first_cap_re.sub(r'\1_\2', name)
        return self.all_cap_re.sub(r'\1_\2', s1).lower()

    def __get_col_names(self):
        return list(map(lambda x: self.__snake_case_from_camel(x[0]), self.cursor.description))

    def execute_all(self, stmt):
        c = self.cursor
        t = c.execute(stmt)
        self.col_names = self.__get_col_names()
        all = t.fetchall()
        named_result = []
        for row in all:
            named = {}
            for idx, col in enumerate(self.col_names):
                named[col] = row[idx]
            named_result.append(named)
        self.close()
        return named_result

    def execute_one(self, stmt):
        c = self.cursor
        t = c.execute(stmt)
        self.col_names = self.__get_col_names()
        one = t.fetchone()
        named_result = {}
        for idx, col in enumerate(self.col_names):
            named_result[col] = one[idx]
        self.close()
        return named_result

    def close(self):
        return self.conn.close()


def _get_type(type_name):
    try:
        type_obj = Type.objects.get(type_name=type_name)
    except:
        type_obj = Type.objects.create_type(type_name)
    return type_obj


@shared_task()
def create_fitting_item(fit, item):
    count = None
    quantity = None
    if 'count' in item:
        count = item['count']

    type_obj = _get_type(item['name'])

    # Dogma Effects
    flags = {11: 'LoSlot', 12: 'HiSlot', 13: 'MedSlot', 2663: 'RigSlot', 3772: 'SubSystemSlot', 6306: 'ServiceSlot'}
    effects = type_obj.dogma_effects.filter(effect_id__in=flags).values_list('effect_id', flat=True)
    effects = list(effects)
    if count is None:
        flag = 'Cargo'
        quantity = item['quantity']
    else:
        flag = flags[effects[0]] + str(count)

    item = FittingItem.objects.create(flag=flag, quantity=quantity if quantity else 1, type_fk=type_obj,
                                      type_id=type_obj.pk, fit=fit)


@shared_task
def create_fit(eft_text, description=None):
    parsed_eft = EftParser(eft_text).parse()

    def __create_fit(ship_type, name, description):
        type_obj = _get_type(ship_type)
        fit = Fitting.objects.create(ship_type=type_obj, ship_type_type_id=type_obj.pk,
                                     name=name, description=description)
        return fit

    fit = __create_fit(parsed_eft['ship'], parsed_eft['name'], description)

    for module in parsed_eft['modules']:
        create_fitting_item(fit, module)

    for item in parsed_eft['cargo_drones']:
        create_fitting_item(fit, item)

def __dgm_attribute_value(da):
    vf = da.pop('value_float')
    vi = da.pop('value_int')
    if vf is not None:
        da['value'] = vf
    elif vi is not None:
        da['value'] = float(vi)

    return da

@shared_task
def populate_types():
    # Get list of type_ids in db
    types = Type.objects.all().values_list('type_id', flat=True)

    # Get SDE
    latest_url = 'https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2'

    latest_req = requests.get(latest_url)
    with open('sde.db.bz2', 'wb') as sde:
        sde.write(latest_req.content)

    open('sde.db', 'wb').write(bz2.open('sde.db.bz2', 'rb').read())

    # Get Types from SDE
    tps = SDEConn().execute_all("select typeID, groupID, typeName, description, mass, volume, capacity, portionSize,"
                                " published, marketGroupID, iconID, graphicID from invTypes;")

    if len(types) > 0:
        objs = [Type(**tp) for tp in tps if tp['type_id'] in types]

        Type.objects.bulk_update(objs, ['type_name', 'description', 'group_id', 'published',
                                        'mass', 'capacity', 'volume', 'packaged_volume',
                                        'portion_size', 'radius', 'graphic_id', 'icon_id',
                                        'market_group_id'], batch_size=500)

        objs = [Type(**tp) for tp in tps if tp['type_id'] not in types]
        dgmA = []
        dgmE = []
        for obj in objs:
            type_id = obj.type_id
            dgmA += [DogmaAttribute(**__dgm_attribute_value(da))
                     for da in SDEConn().execute_all("SELECT * FROM dgmTypeAttributes WHERE typeID = {}".format(type_id))]
            dgmE += [DogmaEffect(**de)
                     for de in SDEConn().execute_all("SELECT * FROM dgmTypeEffects WHERE typeID = {}".format(type_id))]

        # Lets account for an error importing dgm
        dA = DogmaAttribute.objects.all().values_list("type_id", flat=True)
        dE = DogmaEffect.objects.all().values_list("type_id", flat=True)

        # This is a list of type IDs for all types missing from dogmaAttributes or dogmaEffects
        dETypes = [type_ for type_ in types if type_ not in dE]
        dATypes = [type_ for type_ in types if type_ not in dA]
        for dAType in dATypes:
            dgmA += [DogmaAttribute(**__dgm_attribute_value(da))
                     for da in SDEConn().execute_all("SELECT * FROM dgmTypeAttributes WHERE typeID = {}".format(dAType))]
        for dEType in dETypes:
            dgmE += [DogmaEffect(**de)
                     for de in SDEConn().execute_all("SELECT * FROM dgmTypeEffects WHERE typeID = {}".format(dEType))]
    else:
        objs = [Type(**tp) for tp in tps]
        dgmA = [DogmaAttribute(**__dgm_attribute_value(da)) for da in SDEConn().execute_all("SELECT * FROM dgmTypeAttributes")]
        dgmE = [DogmaEffect(**de) for de in SDEConn().execute_all("SELECT * FROM dgmTypeEffects")]

    Type.objects.bulk_create(objs, batch_size=500)
    DogmaEffect.objects.bulk_create(dgmE, batch_size=500)
    DogmaAttribute.objects.bulk_create(dgmA, batch_size=500)

    # Erase file contents to save space
    open('sde.db', 'wb').close()
    open('sde.db.bz2', 'wb').close()





