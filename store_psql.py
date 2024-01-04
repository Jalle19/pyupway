import json
import os
import sys
import argparse
import psycopg2

'''
CREATE TABLE measurement(
id                                          serial not null primary key,
timestamp                                   timestamp with time zone not null default now(),
system_id                                   bigint not null,
"addition temperature BT63"                 float,
"avg. outdoor temp. BT1"                    float,
"blocked"                                   boolean,
"calculated flow temp. S1"                  float,
"comfort mode"                              text,
"compressor operating time EB101"           float,
"compressor operating time hot water EB101" float,
"compressor run time cooling EB101"         float,
"compressor starts EB101"                   float,
"condenser out EB101-BT12"                  float,
"cooling, compr. only."                     float,
"cpr. protection mode EB101"                boolean,
"current BE1"                               float,
"current BE2"                               float,
"current BE3"                               float,
"current compr. frequency EB101"            integer,
"defrosting EB101"                          boolean,
"degree minutes"                            integer,
"electrical addition power"                 float,
"evaporator EB101-BT16"                     float,
"external adjustment S1"                    boolean,
"floor drying function"                     boolean,
"flow BF1"                                  float,
"fuse size"                                 float,
"heat medium flow BT2"                      float,
"heating, compr. only."                     float,
"heating, int. add. incl."                  float,
"high pressure sensor EB101"                float,
"hot gas EB101-BT14"                        float,
"hot water charging BT6"                    float,
"hot water top BT7"                         float,
"hotwater, compr. only."                    float,
"hw, incl. int. add"                        float,
"liquid line EB101-BT15"                    float,
"low pressure sensor EB101"                 float,
"outdoor temp. BT1"                         float,
"outdoor temp. EB101-BT28"                  float,
"pool, compr. only."                        float,
"pump speed heating medium GP1"             integer,
"requested compressor freq EB101"           integer,
"return temp. BT3"                          float,
"return temp. EB101-BT3"                    float,
"set max electrical add."                   float,
"suction gas EB101-BT17"                    float,
"temporary lux"                             boolean,
"time factor"                               float,
"external flow temp. BT25"                  float,
"room temperature BT50"                     float,
"tehowatti addition blocked"                boolean,
"inverter m8 compressor module blocked"     boolean,
"test"                                      integer
)
'''

# map duplicate measurement headers to separate columns
column_mapping = {
    "10033": "tehowatti addition blocked",
    "10014": "inverter m8 compressor module blocked"
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost", help="defaults to localhost")
    parser.add_argument("--port", default=5432, type=int, help="defaults to 5432")
    parser.add_argument("--database", default="myupway", help='defaults to "myupway"')
    args = parser.parse_args()
    username = os.getenv("PSQL_USERNAME")
    password = os.getenv("PSQL_PASSWORD")

    conn = psycopg2.connect(host=args.host, port=args.port, database=args.database, user=username,
                            password=password)

    metrics = json.load(sys.stdin)
    system_id = metrics["system_id"]

    cur = conn.cursor()

    cur.execute("SELECT array_agg(column_name) FROM information_schema.columns "
                "WHERE table_schema = 'public' "
                "  AND table_name   = 'measurement'")
    available_columns = cur.fetchone()[0]

    # Build values to be inserted
    columns = ["system_id"]
    values = [system_id]

    for definition_group_name in metrics["metrics"]:
        definition_group = metrics["metrics"][definition_group_name]

        for key, value in definition_group.items():
            column_name = column_mapping[key] if key in column_mapping else value["name"]

            if column_name in available_columns:
                columns.append(column_name)
                values.append(value["value"])
            else:
                print("Warning: unsupported column \"%s\"" % (column_name))

    column_str = ','.join(map(lambda col: '"%s"' % col.replace('"','""'), columns))
    value_format_str = ','.join(map(lambda col: '%s', columns))

    cur.execute("INSERT INTO measurement (%s) VALUES (%s)" % (column_str, value_format_str),
        tuple(values))

    conn.commit()

    cur.close()
    conn.close()

