#!/usr/bin/python
# -*- coding: latin-1 -*-
import json
import os
import re
import argparse
import sys

import requests

TYPE_TEMPERATURE = "temperature"
TYPE_CURRENT = "current"
TYPE_DIMENSIONLESS = "dimensionless"
TYPE_BOOLEAN_YES_NO = "boolean_yes_no"
TYPE_BOOLEAN_ON_OFF = "boolean_on_off"
TYPE_TIME = "time_period"
TYPE_POWER = "power"
TYPE_ENERGY = "energy"
TYPE_FLOW = "flow"
TYPE_PERCENTAGE = "percentage"
TYPE_PRESSURE = "pressure"
TYPE_FREQUENCY = "frequency"
TYPE_CURRENCY = "currency";
UNIT_DKCURRENCY = "\u00f8re"; # DKK 0.01 unit
UNIT_CURRENCY = UNIT_DKCURRENCY;
UNIT_CELSIUS = "C"
UNIT_AMPERES = "A"
UNIT_DEGREE_MINUTES = "DM"
UNIT_HOURS = "h"
UNIT_KILOWATTS = "kW"
UNIT_KILOWATT_HOURS = "kWh"
UNIT_LITERS_PER_MINUTE = "l/m"
UNIT_PERCENT = "%"
UNIT_BAR = "bar"
UNIT_HERTZ = "Hz"
UNIT_NONE = ""

definition_groups = {
    "tehowatti_status": {
        40067: {"name": "avg. outdoor temp. BT1", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        40014: {"name": "hot water charging BT6", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        40013: {"name": "hot water top BT7", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        40004: {"name": "outdoor temp. BT1", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        40083: {"name": "current BE1", "type": TYPE_CURRENT, "unit": UNIT_AMPERES},
        40081: {"name": "current BE2", "type": TYPE_CURRENT, "unit": UNIT_AMPERES},
        40079: {"name": "current BE3", "type": TYPE_CURRENT, "unit": UNIT_AMPERES},
        43005: {"name": "degree minutes", "type": TYPE_DIMENSIONLESS, "unit": UNIT_DEGREE_MINUTES},
    },
    "tehowatti_hot_water": {
        48132: {"name": "temporary lux", "type": TYPE_BOOLEAN_ON_OFF, "unit": UNIT_NONE},
        47041: {"name": "comfort mode", "type": TYPE_DIMENSIONLESS, "unit": UNIT_NONE},
    },
    "tehowatti_climate_system_1": {
        43161: {"name": "external adjustment S1", "type": TYPE_BOOLEAN_YES_NO, "unit": UNIT_NONE},
        47276: {"name": "floor drying function", "type": TYPE_BOOLEAN_ON_OFF, "unit": UNIT_NONE},
        43009: {"name": "calculated flow temp. S1", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        40071: {"name": "external flow temp. BT25", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        40008: {"name": "heat medium flow BT2", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        40012: {"name": "return temp. BT3", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        40033: {"name": "room temperature BT50", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
    },
    "tehowatti_addition": {
        10033: {"name": "blocked", "type": TYPE_BOOLEAN_YES_NO, "unit": UNIT_NONE},
        47214: {"name": "fuse size", "type": TYPE_CURRENT, "unit": UNIT_AMPERES},
        43081: {"name": "time factor", "type": TYPE_TIME, "unit": UNIT_HOURS},
        43084: {"name": "electrical addition power", "type": TYPE_POWER, "unit": UNIT_KILOWATTS},
        47212: {"name": "set max electrical add.", "type": TYPE_POWER, "unit": UNIT_KILOWATTS},
        40121: {"name": "addition temperature BT63", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
    },
    "tehowatti_heat_meter": {
        44302: {"name": "cooling, compr. only.", "type": TYPE_ENERGY, "unit": UNIT_KILOWATT_HOURS},
        44308: {"name": "heating, compr. only.", "type": TYPE_ENERGY, "unit": UNIT_KILOWATT_HOURS},
        44300: {"name": "heating, int. add. incl.", "type": TYPE_ENERGY, "unit": UNIT_KILOWATT_HOURS},
        44306: {"name": "hotwater, compr. only.", "type": TYPE_ENERGY, "unit": UNIT_KILOWATT_HOURS},
        44298: {"name": "hw, incl. int. add", "type": TYPE_ENERGY, "unit": UNIT_KILOWATT_HOURS},
        44304: {"name": "pool, compr. only.", "type": TYPE_ENERGY, "unit": UNIT_KILOWATT_HOURS},
        40072: {"name": "flow BF1", "type": TYPE_FLOW, "unit": UNIT_LITERS_PER_MINUTE},
    },
    "smart_energy_source": {
        41366: {"name": "compressor", "type": TYPE_DIMENSIONLESS, "unit": UNIT_DEGREE_MINUTES},
        41427: {"name": "price, electricity", "type": TYPE_CURRENCY, "unit": UNIT_CURRENCY},
    },
    "smart_price_adaptation": {
        44896: {"name": "heating", "type": TYPE_DIMENSIONLESS, "unit": UNIT_NONE},
        44897: {"name": "hotwater", "type": TYPE_DIMENSIONLESS, "unit": UNIT_NONE},
        44908: {"name": "hotwater", "type": TYPE_DIMENSIONLESS, "unit": UNIT_NONE},
        10069: {"name": "price of electricity", "type": TYPE_CURRENCY, "unit": UNIT_CURRENCY},

    },
    "soft in/outputs": {
        47411: {"name": "AUX1", "type": TYPE_DIMENSIONLESS, "unit": UNIT_NONE},
        47410: {"name": "AUX2", "type": TYPE_DIMENSIONLESS, "unit": UNIT_NONE},
        47409: {"name": "AUX3", "type": TYPE_DIMENSIONLESS, "unit": UNIT_NONE},
        47408: {"name": "AUX4", "type": TYPE_DIMENSIONLESS, "unit": UNIT_NONE},
        47407: {"name": "AUX5", "type": TYPE_DIMENSIONLESS, "unit": UNIT_NONE},
        47412: {"name": "X7", "type": TYPE_DIMENSIONLESS, "unit": UNIT_NONE},
    },
    "inverter_m8_status": {
        44703: {"name": "defrosting EB101", "type": TYPE_BOOLEAN_YES_NO, "unit": UNIT_NONE},
        44396: {"name": "pump speed heating medium GP1", "type": TYPE_PERCENTAGE, "unit": UNIT_PERCENT},
        44362: {"name": "outdoor temp. EB101-BT28", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
    },
    "inverter_m8_compressor_module": {
        10014: {"name": "blocked", "type": TYPE_BOOLEAN_YES_NO, "unit": UNIT_NONE},
        44069: {"name": "compressor starts EB101", "type": TYPE_DIMENSIONLESS, "unit": UNIT_NONE},
        44866: {"name": "current EB101", "type": TYPE_DIMENSIONLESS, "unit": UNIT_NONE},
        44702: {"name": "cpr. protection mode EB101", "type": TYPE_BOOLEAN_YES_NO, "unit": UNIT_NONE},
        44058: {"name": "condenser out EB101-BT12", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        44363: {"name": "evaporator EB101-BT16", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        41167: {"name": "evaporator EB101-BT84", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        41163: {"name": "high pressure EB101-BP9", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        44059: {"name": "hot gas EB101-BT14", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        44060: {"name": "liquid line EB101-BT15", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        41162: {"name": "low pressure EB101-BP8", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        44055: {"name": "return temp. EB101-BT3", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        44061: {"name": "suction gas EB101-BT17", "type": TYPE_TEMPERATURE, "unit": UNIT_CELSIUS},
        44699: {"name": "high pressure sensor EB101", "type": TYPE_PRESSURE, "unit": UNIT_BAR},
        44700: {"name": "low pressure sensor EB101", "type": TYPE_PRESSURE, "unit": UNIT_BAR},
        44071: {"name": "compressor operating time EB101", "type": TYPE_TIME, "unit": UNIT_HOURS},
        44073: {"name": "compressor operating time hot water EB101", "type": TYPE_TIME, "unit": UNIT_HOURS},
        40737: {"name": "compressor run time cooling EB101", "type": TYPE_TIME, "unit": UNIT_HOURS},
        44701: {"name": "current compr. frequency EB101", "type": TYPE_FREQUENCY, "unit": UNIT_HERTZ},
        40782: {"name": "requested compressor freq EB101", "type": TYPE_FREQUENCY, "unit": UNIT_HERTZ},
        40001: {"name": "test", "type": TYPE_FREQUENCY, "unit": UNIT_HERTZ},
    }
}


def parse_raw_value(raw_value, type, unit):
    if raw_value == "--":
        return None

    if unit == UNIT_CELSIUS:
        return float(re.sub(r'^([-\d.]+)([°º])C$', r'\1', raw_value, flags=re.UNICODE))
    elif unit == UNIT_AMPERES or unit == UNIT_HOURS:
        return float(raw_value[:-1])
    elif unit == UNIT_DEGREE_MINUTES or unit == UNIT_HERTZ:
        return int(raw_value[:-2])
    elif unit == UNIT_KILOWATTS:
        return float(raw_value[:-2])
    elif type == TYPE_BOOLEAN_YES_NO:
        return raw_value == "yes"
    elif type == TYPE_BOOLEAN_ON_OFF:
        return raw_value == "on"
    elif unit == UNIT_KILOWATT_HOURS or unit == UNIT_LITERS_PER_MINUTE or unit == UNIT_BAR:
        return float(raw_value[:-3])
    elif unit == UNIT_PERCENT:
        return int(raw_value[:-1])
    elif unit == UNIT_CURRENCY:
        return float(re.sub(r'^(\d+)(.*)$', r'\1', raw_value, flags=re.UNICODE))

    return raw_value


def get_definition_variables(definition_group):
    return list(definition_group.keys())


def augment_definition_values(definition_group, values):
    for value in values["Values"]:
        varid = int(value["VariableId"])
        if varid in definition_group:
          type = definition_group[varid]["type"]
          unit = definition_group[varid]["unit"]
          definition_group[varid]["value"] = parse_raw_value(value["CurrentValue"], type, unit)

    return definition_group


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--system_id", type=int, help="The system/heat pump ID")
    parser.add_argument("-p", "--prefix", action='store_true', help="Prefix value with time; id; field name in CSV format")
    parser.add_argument("-c", "--currvar", metavar='n', type=int, nargs='+', help="The system variables requested")

    args = parser.parse_args()

    system_id = args.system_id
    currvar = args.currvar
    pref = args.prefix
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    session = requests.session()
    auth_response = session.post("https://myupway.com/LogIn", {
        "returnUrl": f"/System/{system_id}/Status/Overview",
        "Email": email,
        "Password": password
    })

    # The login endpoint doesn't use HTTP 4XX status codes, so we check that it
    # redirects to the "returnUrl" we requested
    redirect = auth_response.history.pop()
    if redirect.headers.get("Location") != f"/System/{system_id}/Status/Overview":
        raise Exception("Authentication failed")

    if not currvar:

      # Start fetching values, one "group" at a time
      for definition_group_name in definition_groups.keys():
        definition_group = definition_groups[definition_group_name]

        values_response = session.post("https://myupway.com/PrivateAPI/Values", {
          "hpid": system_id,
          "variables": get_definition_variables(definition_group)
        })
        values = values_response.json()

        # Augment the definition groups with the values received
        augmented_definition_group = augment_definition_values(definition_group, values)
        definition_groups[definition_group_name] = augmented_definition_group

      metrics = {
        "system_id": system_id,
        "metrics": definition_groups
      }

      print(json.dumps(metrics, indent=2))

    else:
    # retrieve a single or a few current values
    # EMAIL=a@b.c PASSWORD=pwd python3 ./get_metrics.py --system_id 123456 -currvar 44703 44396
    # no
    # 100

      values_response = session.post("https://myupway.com/PrivateAPI/Values", {
        "hpid": system_id,
        "variables": currvar
      })
      values = values_response.json()

      for cv in currvar:
        for def_group_name in definition_groups.keys():
          definition_group = definition_groups[def_group_name]
          if cv in definition_group:
            definition_group = augment_definition_values(definition_group, values)

            if pref:
             # CSV format
              print (values["Date"] + ";" + str(cv) + ";" + definition_group[cv]["name"] +";" + str(definition_group[cv]["value"]))
            else:
            # single value
              print (definition_group[cv]["value"])
