from .models import *
from celery import shared_task


class EftParser:
    def __init__(self, eft_text):
        self.eft_lines = eft_text.strip().splitlines()

    def parse(self):
        modules = []
        cargo_drone = []
        ship_type = ''
        fit_name = ''

        for line in self.eft_lines:
            if line == '':
                continue

            if line.startswith('['):
                if ', ' in line:
                    ship_type, fit_name = line[1:-1].split(', ')

                if 'empty' in line.strip('[]').lower():
                    continue

            else:
                if ', ' in line:
                    module, charge = line.split(', ')
                    modules.append({'module': module, 'charge': charge})
                else:
                    quantity = line.split()[-1]  # Quantity will always be the last element, if it is there.

                    if 'x' in quantity:
                        item_name = line.strip(quantity).strip()
                        cargo_drone.append({'name': item_name, 'quantity': int(quantity.strip('x'))})
                    else:
                        modules.append({'module': line.strip(), 'charge': ''})

        return {'ship': ship_type, 'name': fit_name, 'modules': modules, 'cargo_drones': cargo_drone}


@shared_task
def create_fit(eft_text):
    parsed_eft = EftParser(eft_text).parse()
