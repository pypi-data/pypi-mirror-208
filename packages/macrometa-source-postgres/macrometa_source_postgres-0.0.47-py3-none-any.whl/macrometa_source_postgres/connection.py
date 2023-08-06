import datetime
import decimal
import json
import math
from typing import List

import psycopg2
import psycopg2.extras
import pytz
import singer
from dateutil.parser import parse

LOGGER = singer.get_logger('macrometa_source_postgres')
CURSOR_ITER_SIZE = 20000

def calculate_destination_stream_name(stream, md_map):
    return f"{md_map.get((), {}).get('schema-name')}-{stream['stream']}"


def canonicalize_identifier(identifier):
    """
    Canonicalizes the given identifier according to PostgreSQL documentation.
    Quoted identifiers can contain any character, except the character with code zero.
    To include a double quote, write two double quotes.
    """
    return identifier.replace('"', '""')


def fully_qualified_column_name(schema, table, column):
    return f'"{canonicalize_identifier(schema)}"."{canonicalize_identifier(table)}"."{canonicalize_identifier(column)}"'


def fully_qualified_table_name(schema, table):
    return f'"{canonicalize_identifier(schema)}"."{canonicalize_identifier(table)}"'


def connect(conn_config, logical_replication=False, prioritize_primary=False):
    """
    Opens a connection to the PostgreSQL database using the given configuration
    """
    cfg = {
        'application_name': 'macrometa',
        'host': conn_config['host'],
        'dbname': conn_config['dbname'],
        'user': conn_config['user'],
        'password': conn_config['password'],
        'port': conn_config['port'],
        'connect_timeout': 30
    }

    if conn_config['use_secondary'] and not prioritize_primary and not logical_replication:
        # Attempt to use the replica for connection, but fall back to the primary if necessary
        # (e.g., if replica keys are missing in the configuration)
        cfg['host'] = conn_config.get("secondary_host", conn_config['host'])
        cfg['port'] = conn_config.get("secondary_port", conn_config['port'])

    if conn_config.get('ssl'):
        cfg['sslmode'] = 'require'
        if conn_config.get('ssl_root_ca_cert'):
            cfg['sslrootcert'] = conn_config['ssl_root_ca_cert']
        if conn_config.get('ssl_client_certificate'):
            cfg['sslcert'] = conn_config['ssl_client_certificate']
            if conn_config.get('ssl_client_key'):
                cfg['sslkey'] = conn_config['ssl_client_key']
            if conn_config.get('ssl_client_password'):
                cfg['sslpassword'] = conn_config['ssl_client_password']

    if logical_replication:
        cfg['connection_factory'] = psycopg2.extras.LogicalReplicationConnection

    return psycopg2.connect(**cfg)


def prepare_columns_for_select_sql(c, md_map):
    column_name = f' "{canonicalize_identifier(c)}" '
    prop_metadata = md_map.get(('properties', c), {})

    if 'sql-datatype' in prop_metadata:
        sql_datatype = prop_metadata['sql-datatype']
        if sql_datatype.startswith('timestamp') and not sql_datatype.endswith('[]'):
            return f'CASE ' \
                   f'WHEN {column_name} < \'0001-01-01 00:00:00.000\' ' \
                   f'OR {column_name} > \'9999-12-31 23:59:59.999\' THEN \'9999-12-31 23:59:59.999\' ' \
                   f'ELSE {column_name} ' \
                   f'END AS {column_name}'

    return column_name


def prepare_columns_sql(c):
    return f""" "{canonicalize_identifier(c)}" """


def filter_schemas_sql_clause(sql, filer_schemas):
    in_clause = " AND n.nspname in (" + ",".join([f"'{b.strip(' ')}'" for b in filer_schemas.split(',')]) + ")"
    return sql + in_clause


def clean_time_with_time_zone(elem):
    elem = str(elem)
    if elem.startswith('24'):
        elem = elem.replace('24', '00', 1)
    elem = datetime.datetime.strptime(elem, '%H:%M:%S%z')
    if elem.utcoffset() != datetime.timedelta(seconds=0):
        LOGGER.warning('time with time zone values are converted to UTC')
    elem = elem.astimezone(pytz.utc)
    elem = str(elem.strftime('%H:%M:%S'))
    return parse(elem).isoformat().split('T')[1]

def clean_time_without_time_zone(elem):
    elem = str(elem)
    if elem.startswith('24'):
        elem = elem.replace('24', '00', 1)
    return parse(elem).isoformat().split('T')[1]

def clean_datetime(elem, sql_datatype):
    if sql_datatype == 'timestamp with time zone':
        return elem.isoformat()
    else:  # timestamp WITHOUT time zone
        return f'{elem.isoformat()}+00:00'

def clean_float(elem):
    return None if math.isnan(elem) or math.isinf(elem) else elem

def convert_value_to_singer_value(elem, sql_datatype):
    sql_datatype = sql_datatype.replace('[]', '')

    if elem is None:
        return elem

    type_cleaning_map = {
        'money': lambda: elem,
        'json': lambda: json.loads(elem),
        'jsonb': lambda: json.loads(elem),
        'time with time zone': lambda: clean_time_with_time_zone(elem),
        'time without time zone': lambda: clean_time_without_time_zone(elem),
        'bit': lambda: elem == '1',
        'boolean': lambda: elem
    }

    if sql_datatype in type_cleaning_map:
        return type_cleaning_map[sql_datatype]()

    if isinstance(elem, (datetime.datetime, datetime.date)):
        return clean_datetime(elem, sql_datatype)

    if isinstance(elem, (int, str, datetime.time)):
        return elem

    if isinstance(elem, decimal.Decimal):
        return None if elem.is_nan() else elem

    if isinstance(elem, float):
        return clean_float(elem)

    if isinstance(elem, dict):
        if sql_datatype == 'hstore':
            return elem
        else:
            raise Exception(f"do not know how to marshall a dict if its not an hstore or json: {sql_datatype}")

    raise Exception(
        f"do not know how to marshall value of class( {elem.__class__} ) and sql_datatype ( {sql_datatype} )")


def convert_array_to_singer_value(elem, sql_datatype):
    if isinstance(elem, list):
        return list(map(lambda elem: convert_array_to_singer_value(elem, sql_datatype), elem))

    return convert_value_to_singer_value(elem, sql_datatype)


def convert_values_to_singer_values(elem, sql_datatype):
    # Check if the given SQL datatype is an array
    if '[]' in sql_datatype:
        # If it's an array, convert each element to the appropriate Singer value
        array_elements = elem or []
        return [convert_array_to_singer_value(item, sql_datatype) for item in array_elements]

    # If it's not an array, convert the value directly using the implementation function
    return convert_value_to_singer_value(elem, sql_datatype)


def selected_row_to_singer_message(stream, row, version, columns, time_extracted, md_map):
    row_to_persist = ()
    for idx, elem in enumerate(row):
        sql_datatype = md_map.get(('properties', columns[idx]))['sql-datatype']
        cleaned_elem = convert_values_to_singer_values(elem, sql_datatype)
        row_to_persist += (cleaned_elem,)

    rec = dict(zip(columns, row_to_persist))

    return singer.RecordMessage(
        stream=calculate_destination_stream_name(stream, md_map),
        record=rec,
        version=version,
        time_extracted=time_extracted)


def hstore_available(conn_info):
    with connect(conn_info) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor, name='macrometa_cursor') as cur:
            cur.execute(""" SELECT installed_version FROM pg_available_extensions WHERE name = 'hstore' """)
            res = cur.fetchone()
            return bool(res and res[0])


def compute_source_stream_id(schema_name, table_name):
    return f'{schema_name}-{table_name}'


# Constants for maximum scale and precision for numeric/decimal columns in PostgreSQL
MAX_SCALE = 38
MAX_PRECISION = 100


def numeric_precision(c):
    if c.numeric_precision is None:
        return MAX_PRECISION

    if c.numeric_precision > MAX_PRECISION:
        LOGGER.warning('capping decimal precision to 100.  THIS MAY CAUSE TRUNCATION')
        return MAX_PRECISION

    return c.numeric_precision


def numeric_scale(c):
    if c.numeric_scale is None:
        return MAX_SCALE
    if c.numeric_scale > MAX_SCALE:
        LOGGER.warning('capping decimal scale to 38.  THIS MAY CAUSE TRUNCATION')
        return MAX_SCALE

    return c.numeric_scale


def numeric_multiple_of(scale):
    return 10 ** (0 - scale)


def numeric_max(precision, scale):
    return 10 ** (precision - scale)


def numeric_min(precision, scale):
    return -10 ** (precision - scale)


def filter_tables_sql_clause(sql, tables: List[str]):
    in_clause = " AND pg_class.relname in (" + ",".join([f"'{b.strip(' ')}'" for b in tables]) + ")"
    return sql + in_clause
