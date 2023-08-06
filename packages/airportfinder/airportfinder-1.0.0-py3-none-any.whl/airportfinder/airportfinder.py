from pkg_resources import resource_string
import json
import re
import logging

logger = logging.getLogger(__name__)

class Airports:
    def __init__(self):
        airports_json = resource_string('airportfinder', 'data/airports.json')
        airports_data = json.loads(airports_json)
        self.airports_iata = {airport['code']: airport for airport in airports_data}
        self.airports_name = {airport['name']: airport for airport in airports_data}

    @staticmethod
    def _validate(value, field_name):
        if not isinstance(value, str):
            raise ValueError("{0} must be a string, it is a {1}".format(field_name, type(value)))
        value = value.strip()
        if not value:
            raise ValueError("{0} cannot be empty".format(field_name))
        if field_name == 'iata' and not re.match(r'^[A-Z]{3}$', value):
            raise ValueError("Invalid IATA code: {0}".format(value))
        return value

    def airport_iata(self, iata):
        iata = self._validate(iata, "iata") if iata is not None else None
        aiport_obj = self.airports_iata.get(iata)
        if not aiport_obj:
            logger.error("Airport not found with iata: %s", iata)
            return None
        return aiport_obj

    def airport_name(self, name):
        name = self._validate(name, "name") if name is not None else None
        aiport_obj = self.airports_name.get(name)
        if not aiport_obj:
            logger.error("Airport not found with name: %s", name)
            return None
        return aiport_obj

