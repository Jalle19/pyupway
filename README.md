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
INFLUX_USERNAME=myupway INFLUX_PASSWORD=myupway python3 store_influxdb.py --host 10.110.1.6
```
