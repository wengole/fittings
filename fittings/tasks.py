import os
import requests
import bz2
import sqlite3
import re

from .models import Fitting, FittingItem, Type, DogmaEffect, DogmaAttribute
from .providers import esi
from celery import shared_task
from concurrent.futures import ThreadPoolExecutor, as_completed
from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class EftParser:
    def __init__(self, eft_text):
        self.eft_lines = eft_text.strip().splitlines()

    def parse(self):
        sections = []
        for section in _importSectionIter(self.eft_lines):
            sections.append(section)

        modules = []
        cargo = []
        drone_bay = []
        fighter_bay = []
        ship_type = ""
        fit_name = ""
        counter = 0  # Slot flag number
        last_line = ""
        end_fit = False

        for section in sections:
            counter = 0
            if section.isDroneBay():
                for line in section.lines:
                    quantity = line.split()[-1]
                    item_name = line.split(quantity)[0].strip()
                    drone_bay.append(
                        {
                            "name": item_name,
                            "quantity": int(quantity.strip("x")),
                            "section_name": "DroneBay",
                        }
                    )
            elif section.isFighterBay():
                for line in section.lines:
                    quantity = line.split()[-1]
                    item_name = line.split(quantity)[0].strip()
                    fighter_bay.append(
                        {
                            "name": item_name,
                            "quantity": int(quantity.strip("x")),
                            "section_name": "FighterBay",
                        }
                    )
            else:
                for line in section.lines:
                    if line.startswith("["):
                        if ", " in line:
                            ship_type, fit_name = line[1:-1].split(", ")
                            continue

                        if "empty" in line.strip("[]").lower():
                            continue
                    else:
                        if "," in line:
                            module, charge = line.split(",")
                            modules.append(
                                {
                                    "name": module,
                                    "charge": charge.strip(),
                                    "count": counter,
                                }
                            )
                        else:

                            quantity = line.split()[
                                -1
                            ]  # Quantity will always be the last element, if it is there.

                            if "x" in quantity and quantity[1:].isdigit():
                                item_name = line.split(quantity)[0].strip()
                                cargo.append(
                                    {
                                        "name": item_name,
                                        "quantity": int(quantity.strip("x")),
                                        "section_name": "Cargo",
                                    }
                                )
                            elif end_fit is True:
                                cargo.append(
                                    {
                                        "name": line.strip(),
                                        "quantity": 1,
                                        "section_name": "Cargo",
                                    }
                                )
                            else:
                                modules.append(
                                    {
                                        "name": line.strip(),
                                        "charge": "",
                                        "count": counter,
                                    }
                                )
                    counter += 1

        return {
            "ship": ship_type,
            "name": fit_name,
            "modules": modules,
            "cargo": cargo,
            "drone_bay": drone_bay,
            "fighter_bay": fighter_bay,
        }


def _importSectionIter(lines):
    section = Section()
    for line in lines:
        if not line:
            if section.lines:
                yield section
                section = Section()
        else:
            section.lines.append(line)
    if section.lines:
        yield section


class Section:
    def __init__(self):
        self.lines = []

    def isDroneBay(self):

        types = []
        for line in self.lines:
            if line.startswith("["):
                return False
            quantity = line.split()[-1]
            if "x" in quantity and quantity[1:].isdigit():
                types.append(_get_type(line.split(quantity)[0].strip()))
            else:
                types.append(_get_type(line.strip()))
        return all(
            _type is not None and _type.group.category_id == 18 for _type in types
        )

    def isFighterBay(self):
        types = []
        for line in self.lines:
            if line.startswith("["):
                return False
            quantity = line.split()[-1]
            if "x" in quantity and quantity[1:].isdigit():
                types.append(_get_type(line.split(quantity)[0].strip()))
            else:
                types.append(_get_type(line.strip()))
        return all(
            _type is not None and _type.group.category_id == 87 for _type in types
        )


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
    if "count" in item:
        count = item["count"]

    type_obj = _get_type(item["name"])

    # Dogma Effects
    flags = {
        11: "LoSlot",
        12: "HiSlot",
        13: "MedSlot",
        2663: "RigSlot",
        3772: "SubSystemSlot",
        6306: "ServiceSlot",
    }
    effects = type_obj.dogma_effects.filter(effect_id__in=flags).values_list(
        "effect_id", flat=True
    )
    effects = list(effects)
    if count is None:
        flag = item["section_name"]
        quantity = item["quantity"]
    else:
        flag = flags[effects[0]] + str(count)

    item = FittingItem.objects.create(
        flag=flag,
        quantity=quantity if quantity else 1,
        type_fk=type_obj,
        type_id=type_obj.pk,
        fit=fit,
    )


@shared_task
def create_fit(eft_text, description=None):
    parsed_eft = EftParser(eft_text).parse()

    logger.info("Creating fit.")
    logger.debug(f"Fit name: {parsed_eft['name']}, Type: {parsed_eft['ship']}")

    def __create_fit(ship_type, name, description):
        type_obj = _get_type(ship_type)
        fit = Fitting.objects.create(
            ship_type=type_obj,
            ship_type_type_id=type_obj.pk,
            name=name,
            description=description,
        )
        return fit

    fit = __create_fit(parsed_eft["ship"], parsed_eft["name"], description)
    create_fitting_items(fit, parsed_eft)

    logger.info("Done creating fit.")


@shared_task
def create_fitting_items(fit, parsed_eft):
    type_names = [x["name"] for x in parsed_eft["modules"]]
    type_names += [x["name"] for x in parsed_eft["cargo"]]
    type_names += [x["name"] for x in parsed_eft["drone_bay"]]
    type_names += [x["name"] for x in parsed_eft["fighter_bay"]]
    type_names = list(set(type_names))

    # Get a list of types missing from the db
    types = Type.objects.filter(type_name__in=type_names).values_list(
        "type_name", flat=True
    )

    missing = [x for x in type_names if x not in types]

    # Create missing types
    _processes = []
    with ThreadPoolExecutor(
        max_workers=50
    ) as ex:  # Number of workers might need to be tweaked over time.
        for name in missing:
            _processes.append(ex.submit(Type.objects.create_type, name))

    for item in as_completed(_processes):
        _ = item.result()

    # Create the fitting items
    for module in parsed_eft["modules"]:
        create_fitting_item(fit, module)

    for item in parsed_eft["cargo"]:
        create_fitting_item(fit, item)

    for item in parsed_eft["drone_bay"]:
        create_fitting_item(fit, item)

    for item in parsed_eft["fighter_bay"]:
        create_fitting_item(fit, item)


@shared_task
def update_fit(eft_text, fit_id, description=None):
    parsed_eft = EftParser(eft_text).parse()
    fit = Fitting.objects.get(id=fit_id)

    if parsed_eft["ship"] != fit.ship_type.type_name:
        logger.info("Cannot update a fitting with different ship type")
        return

    logger.info("Updating Fit name: {parsed_eft['name']}, Type: {parsed_eft['ship']}")

    FittingItem.objects.filter(fit__id=fit_id).delete()

    create_fitting_items(fit, parsed_eft)

    fit.name = parsed_eft["name"]
    fit.description = description
    fit.save()

    logger.info("Done updating fit " + fit_id)


@shared_task
def missing_group_type_fix():
    logger.info("Started updating groups for preexisting types.")
    # Grab all types with a null group field.
    types = Type.objects.filter(group=None)

    _processes = []
    with ThreadPoolExecutor(max_workers=50) as ex:
        for _type in types:
            _processes.append(
                ex.submit(Type.objects.create_type_from_id, _type.type_id)
            )

    for item in as_completed(_processes):
        _ = item.result()

    logger.info("Done updating groups.")
