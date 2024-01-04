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
);

-- optional
CREATE TABLE sample_metadata(
id                                          serial not null primary key,
measurement_id                              serial not null references measurement(id),
definition_group                            varchar(256) not null,
system_offline                              boolean not null,
sample_timestamp                            timestamp with time zone not null
);
'''

# map duplicate measurement headers to separate columns
column_mapping = {
    "10033": "tehowatti addition blocked",
    "10014": "inverter m8 compressor module blocked"
}


def get_column_insert_definitions(columns):
    column_str = ','.join(map(lambda col: '"%s"' % col.replace('"','""'), columns))
    value_format_str = ','.join(map(lambda col: '%s', columns))

    return (column_str, value_format_str)


def insert_sample_metadata(cursor, measurement_id, metadata):
    for definition_group_name in metadata:
        definition_group = metadata[definition_group_name]

        # Build values to be inserted
        columns = ["measurement_id", "definition_group"]
        values = [measurement_id, definition_group_name]

        for key, value in definition_group.items():
            columns.append(key)
            values.append(value)

        (column_str, value_format_str) = get_column_insert_definitions(columns)

        cursor.execute("INSERT INTO sample_metadata (%s) VALUES (%s)" % (column_str, value_format_str),
            tuple(values))


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

    (column_str, value_format_str) = get_column_insert_definitions(columns)

    cur.execute("INSERT INTO measurement (%s) VALUES (%s) RETURNING id" % (column_str, value_format_str),
        tuple(values))

    measurement_id = cur.fetchone()[0]

    cur.execute("""SELECT EXISTS (
                       SELECT FROM information_schema.tables
                       WHERE table_schema = 'public'
                           AND table_name = 'sample_metadata'
                   )""")

    have_sample_metadata_table = cur.fetchone()[0]

    if have_sample_metadata_table and "metadata" in metrics:
        insert_sample_metadata(cur, measurement_id, metrics["metadata"])

    conn.commit()

    cur.close()
    conn.close()

