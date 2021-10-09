# pyupway

Collection of utilities for extracting Jäspi heating system metrics through their rebranded Nibe Uplink service called 
myUpway. The metrics can be ingested into InfluxDB.

## Requirements

* Python 3.8 (may work with older versions)

## Installation

```bash
pip3 install -r requirements.txt
```

## get_metrics.py

Fetches all available metrics from myUpway and outputs them as JSON.

Usage:

```bash
$ python3 get_metrics.py --help
usage: get_metrics.py [-h] [-s SYSTEM_ID]

optional arguments:
  -h, --help            show this help message and exit
  -s SYSTEM_ID, --system_id SYSTEM_ID
                        The system/heat pump ID
```

Example:

```bash
EMAIL=user@example.com PASSWORD=password python3 get_metrics.py --system_id 123456
```

Example output can be found in [examples/metrics.json](examples/metrics.json).

## store_influxdb.py

Stores metrics in InfluxDB.

Usage:

```bash
$ python3 store_influxdb.py --help
usage: store_influxdb.py [-h] [--host HOST] [--port PORT] [--database DATABASE]

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          defaults to localhost
  --port PORT          defaults to 8086
  --database DATABASE  defaults to "myupway"
```

Example:

```bash
cat examples/metrics.json | INFLUX_USERNAME=myupway INFLUX_PASSWORD=myupway python3 store_influxdb.py --host 10.110.1.6
```

Field keys and data types:

```
fieldKey                                  fieldType
--------                                  ---------
addition temperature BT63                 float
avg. outdoor temp. BT1                    float
blocked                                   boolean
calculated flow temp. S1                  float
comfort mode                              string
compressor operating time EB101           float
compressor operating time hot water EB101 float
compressor run time cooling EB101         float
compressor starts EB101                   string
condenser out EB101-BT12                  float
cooling, compr. only.                     float
cpr. protection mode EB101                boolean
current BE1                               float
current BE2                               float
current BE3                               float
current compr. frequency EB101            integer
defrosting EB101                          boolean
degree minutes                            integer
electrical addition power                 float
evaporator EB101-BT16                     float
external adjustment S1                    boolean
floor drying function                     boolean
flow BF1                                  float
fuse size                                 float
heat medium flow BT2                      float
heating, compr. only.                     float
heating, int. add. incl.                  float
high pressure sensor EB101                float
hot gas EB101-BT14                        float
hot water charging BT6                    float
hot water top BT7                         float
hotwater, compr. only.                    float
hw, incl. int. add                        float
liquid line EB101-BT15                    float
low pressure sensor EB101                 float
outdoor temp. BT1                         float
outdoor temp. EB101-BT28                  float
pool, compr. only.                        float
pump speed heating medium GP1             integer
requested compressor freq EB101           integer
return temp. BT3                          float
return temp. EB101-BT3                    float
set max electrical add.                   float
suction gas EB101-BT17                    float
temporary lux                             boolean
time factor                               float
```