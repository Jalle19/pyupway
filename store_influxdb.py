import json
import os
import sys
import argparse
from influxdb import InfluxDBClient

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost", help="defaults to localhost")
    parser.add_argument("--port", default=8086, type=int, help="defaults to 8086")
    parser.add_argument("--database", default="myupway", help='defaults to "myupway"')
    args = parser.parse_args()
    username = os.getenv("INFLUX_USERNAME")
    password = os.getenv("INFLUX_PASSWORD")

    influx = InfluxDBClient(host=args.host, port=args.port, database=args.database, username=username,
                            password=password)

    metrics = json.load(sys.stdin)
    system_id = metrics["system_id"]

    # Build tag and field set
    tags = {
        "system_id": system_id
    }

    fields = {

    }

    # Add one field per definition,
    for definition_group_name in metrics["metrics"]:
        definition_group = metrics["metrics"][definition_group_name]

        for value in definition_group.values():
            fields[value["name"]] = value["value"]

    influx.write_points([
        {
            "measurement": "myupway",
            "tags": {
                "system_id": system_id,
            },
            "fields": fields,
        }
    ])
