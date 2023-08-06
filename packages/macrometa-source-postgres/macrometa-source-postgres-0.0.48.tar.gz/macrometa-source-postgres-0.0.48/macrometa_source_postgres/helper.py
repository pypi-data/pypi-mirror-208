import collections
import copy
import json
import sys
import singer
from typing import Dict, List, Optional

import psycopg2.extras
from singer import metadata

import macrometa_source_postgres.connection as postgres
from macrometa_source_postgres.connection import connect


LOGGER = singer.get_logger('macrometa_source_postgres')

# Postgres Logminer does not support certain datatypes, including LONG, LONG RAW, CLOB, BLOB, NCLOB, ADT, or COLLECTION.
Column = collections.namedtuple('Column', [
    "column_name",
    "is_primary_key",
    "sql_data_type",
    "character_maximum_length",
    "numeric_precision",
    "numeric_scale",
    "is_array",
    "is_enum"

])

INTEGER_TYPES = {'integer', 'smallint', 'bigint'}
FLOAT_TYPES = {'real', 'double precision'}
JSON_TYPES = {'json', 'jsonb'}
BASE_RECURSIVE_SCHEMAS = {
    'sdc_recursive_integer_array': {'type': ['null', 'integer', 'array'],
                                    'items': {'$ref': '#/definitions/sdc_recursive_integer_array'}},
    'sdc_recursive_number_array': {'type': ['null', 'number', 'array'],
                                   'items': {'$ref': '#/definitions/sdc_recursive_number_array'}},
    'sdc_recursive_string_array': {'type': ['null', 'string', 'array'],
                                   'items': {'$ref': '#/definitions/sdc_recursive_string_array'}},
    'sdc_recursive_boolean_array': {'type': ['null', 'boolean', 'array'],
                                    'items': {'$ref': '#/definitions/sdc_recursive_boolean_array'}},
    'sdc_recursive_timestamp_array': {'type': ['null', 'string', 'array'],
                                      'format': 'date-time',
                                      'items': {'$ref': '#/definitions/sdc_recursive_timestamp_array'}},
    'sdc_recursive_object_array': {'type': ['null', 'object', 'array'],
                                   'items': {'$ref': '#/definitions/sdc_recursive_object_array'}}
}


def discover_db(connection, filter_schemas=None, tables: Optional[List[str]] = None):
    """
    Discover database streams by extracting table information from the database cluster
    and returning column details. If given, only returns details for the specified tables.
    Optionally filters schema names to discover from the database cluster.
    """
    table_info = produce_table_info(connection, filter_schemas, tables)
    return discover_columns(connection, table_info)


def produce_table_info(conn, filter_schemas=None, tables: Optional[List[str]] = None):
    """
    Generates information about the tables in the database.

    This function fetches information about tables, including their schema names, table names, column names,
    data types, and other relevant attributes. It returns a dictionary containing this information, which can
    be used for further processing.

    :param conn: A connection object to the database.
    :param filter_schemas: An optional list of schema names to filter the results.
    :param tables: An optional list of table names to filter the results.
    :return: A dictionary containing information about the tables in the database.
    """

    # Using the cursor to fetch table and column information from the database.

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor, name='macrometa_cursor') as cur:
        cur.itersize = postgres.CURSOR_ITER_SIZE
        table_info = {}
        sql = """
SELECT
  pg_class.reltuples::BIGINT                            AS approximate_row_count,
  (pg_class.relkind = 'v' or pg_class.relkind = 'm')    AS is_view,
  n.nspname                                             AS schema_name,
  pg_class.relname                                      AS table_name,
  attname                                               AS column_name,
  i.indisprimary                                        AS primary_key,
  format_type(a.atttypid, NULL::integer)                AS data_type,
  information_schema._pg_char_max_length(CASE WHEN COALESCE(subpgt.typtype, pgt.typtype) = 'd'
                                              THEN COALESCE(subpgt.typbasetype, pgt.typbasetype) ELSE COALESCE(subpgt.oid, pgt.oid)
                                          END,
                                          information_schema._pg_truetypmod(a.*, pgt.*))::information_schema.cardinal_number AS character_maximum_length,
  information_schema._pg_numeric_precision(CASE WHEN COALESCE(subpgt.typtype, pgt.typtype) = 'd'
                                                THEN COALESCE(subpgt.typbasetype, pgt.typbasetype) ELSE COALESCE(subpgt.oid, pgt.oid)
                                            END,
                                           information_schema._pg_truetypmod(a.*, pgt.*))::information_schema.cardinal_number AS numeric_precision,
  information_schema._pg_numeric_scale(CASE WHEN COALESCE(subpgt.typtype, pgt.typtype) = 'd'
                                                THEN COALESCE(subpgt.typbasetype, pgt.typbasetype) ELSE COALESCE(subpgt.oid, pgt.oid)
                                        END,
                                       information_schema._pg_truetypmod(a.*, pgt.*))::information_schema.cardinal_number AS numeric_scale,
  pgt.typcategory                       = 'A' AS is_array,
  COALESCE(subpgt.typtype, pgt.typtype) = 'e' AS is_enum
FROM pg_attribute a
LEFT JOIN pg_type AS pgt ON a.atttypid = pgt.oid
JOIN pg_class
  ON pg_class.oid = a.attrelid
JOIN pg_catalog.pg_namespace n
  ON n.oid = pg_class.relnamespace
LEFT OUTER JOIN pg_index as i
  ON a.attrelid = i.indrelid
 AND a.attnum = ANY(i.indkey)
 AND i.indisprimary = true
LEFT OUTER JOIN pg_type AS subpgt
  ON pgt.typelem = subpgt.oid
 AND pgt.typelem != 0
WHERE attnum > 0
AND NOT a.attisdropped
AND pg_class.relkind IN ('r', 'v', 'm', 'p')
AND n.nspname NOT in ('pg_toast', 'pg_catalog', 'information_schema')
AND has_column_privilege(pg_class.oid, attname, 'SELECT') = true """

        if filter_schemas:
            sql = postgres.filter_schemas_sql_clause(sql, filter_schemas)

        if tables:
            sql = postgres.filter_tables_sql_clause(sql, tables)

        cur.execute(sql)

        for row in cur.fetchall():
            row_count, is_view, schema_name, table_name, *col_info = row

            if table_info.get(schema_name) is None:
                table_info[schema_name] = {}

            if table_info[schema_name].get(table_name) is None:
                table_info[schema_name][table_name] = {'is_view': is_view, 'row_count': row_count, 'columns': {}}

            col_name = col_info[0]

            table_info[schema_name][table_name]['columns'][col_name] = Column(*col_info)

        return table_info


def discover_columns(connection, table_info):
    """
    Generates more info about columns of the given table
    """
    entries = []
    for schema_name in table_info.keys():
        for table_name in table_info[schema_name].keys():

            mdata = {}
            columns = table_info[schema_name][table_name]['columns']
            table_pks = [col_name for col_name, col_info in columns.items() if col_info.is_primary_key]
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(" SELECT current_database()")
                database_name = cur.fetchone()[0]

            metadata.write(mdata, (), 'table-key-properties', table_pks)
            metadata.write(mdata, (), 'schema-name', schema_name)
            metadata.write(mdata, (), 'database-name', database_name)
            metadata.write(mdata, (), 'row-count', table_info[schema_name][table_name]['row_count'])
            metadata.write(mdata, (), 'is-view', table_info[schema_name][table_name].get('is_view'))

            column_schemas = {col_name: build_column_schema(col_info) for col_name, col_info in columns.items()}

            schema = {'type': 'object',
                      'properties': column_schemas,
                      'definitions': {}}

            schema = include_array_schemas(columns, schema)

            for c_name in column_schemas:
                mdata = write_sql_data_type_md(mdata, columns[c_name])

                if column_schemas[c_name].get('type') is None:
                    mdata = metadata.write(mdata, ('properties', c_name), 'inclusion', 'unsupported')
                    mdata = metadata.write(mdata, ('properties', c_name), 'selected-by-default', False)
                elif table_info[schema_name][table_name]['columns'][c_name].is_primary_key:
                    mdata = metadata.write(mdata, ('properties', c_name), 'inclusion', 'automatic')
                    mdata = metadata.write(mdata, ('properties', c_name), 'selected-by-default', True)
                else:
                    mdata = metadata.write(mdata, ('properties', c_name), 'inclusion', 'available')
                    mdata = metadata.write(mdata, ('properties', c_name), 'selected-by-default', True)

            entry = {'table_name': table_name,
                     'stream': table_name,
                     'metadata': metadata.to_list(mdata),
                     'tap_stream_id': postgres.compute_source_stream_id(schema_name, table_name),
                     'schema': schema}

            entries.append(entry)

    return entries


def build_column_schema_datatype(col):
    """
    Build json schema for columns with non-array datatype
    """
    schema = {}
    # Only schema non array datatype is built here
    data_type = col.sql_data_type.lower().replace('[]', '')

    if data_type in INTEGER_TYPES:
        schema['type'] = nullable_column('integer', col.is_primary_key)
        schema['minimum'] = -1 * (2 ** (col.numeric_precision - 1))
        schema['maximum'] = 2 ** (col.numeric_precision - 1) - 1
        return schema

    if data_type == 'money':
        schema['type'] = nullable_column('string', col.is_primary_key)
        return schema
    if col.is_enum:
        schema['type'] = nullable_column('string', col.is_primary_key)
        return schema

    if data_type == 'bit' and col.character_maximum_length == 1:
        schema['type'] = nullable_column('boolean', col.is_primary_key)
        return schema

    if data_type == 'boolean':
        schema['type'] = nullable_column('boolean', col.is_primary_key)
        return schema

    if data_type == 'uuid':
        schema['type'] = nullable_column('string', col.is_primary_key)
        return schema

    if data_type == 'hstore':
        schema['type'] = nullable_column('object', col.is_primary_key)
        schema['properties'] = {}
        return schema

    if data_type == 'citext':
        schema['type'] = nullable_column('string', col.is_primary_key)
        return schema

    if data_type in JSON_TYPES:
        schema['type'] = nullable_columns(['object', 'array'], col.is_primary_key)
        return schema

    if data_type == 'numeric':
        return build_column_schema_datatype_numeric(col, schema)

    if data_type in {'time without time zone', 'time with time zone'}:
        return build_column_schema_datatype_time(col, schema, 'time')

    if data_type in ('date', 'timestamp without time zone', 'timestamp with time zone'):
        return build_column_schema_datatype_time(
            col, schema, 'date-time'
        )

    if data_type in FLOAT_TYPES:
        schema['type'] = nullable_column('number', col.is_primary_key)
        return schema

    if data_type == 'text':
        schema['type'] = nullable_column('string', col.is_primary_key)
        return schema

    if data_type == 'character varying':
        return build_column_schema_datatype_character(col, schema)

    if data_type == 'character':
        return build_column_schema_datatype_character(col, schema)

    if data_type in {'cidr', 'inet', 'macaddr'}:
        schema['type'] = nullable_column('string', col.is_primary_key)
        return schema

    return schema


def build_column_schema_datatype_numeric(col, schema):
    schema['type'] = nullable_column('number', col.is_primary_key)
    scale = postgres.numeric_scale(col)
    precision = postgres.numeric_precision(col)

    schema['exclusiveMaximum'] = True
    schema['maximum'] = postgres.numeric_max(precision, scale)
    schema['multipleOf'] = postgres.numeric_multiple_of(scale)
    schema['exclusiveMinimum'] = True
    schema['minimum'] = postgres.numeric_min(precision, scale)
    return schema


def build_column_schema_datatype_character(col, schema):
    schema['type'] = nullable_column('string', col.is_primary_key)
    if col.character_maximum_length:
        schema['maxLength'] = col.character_maximum_length

    return schema


def build_column_schema_datatype_time(col, schema, arg2):
    schema['type'] = nullable_column('string', col.is_primary_key)
    schema['format'] = arg2
    return schema


def build_column_schema(col_info):
    """
    Build JSON schema for the given column.
    """
    column_schema = {'type': ["null", "array"]}

    if not col_info.is_array:
        return build_column_schema_datatype(col_info)

    def type_suffix(type_name):
        return type_name[:-2] if type_name.endswith('[]') else type_name

    def schema_ref(type_name):
        return f'#/definitions/sdc_recursive_{type_suffix(type_name)}_array'

    sql_data_type_map = {
        f'{int_type}[]': schema_ref('integer') for int_type in INTEGER_TYPES
    }
    sql_data_type_map.update({
        f'{float_type}[]': schema_ref('number') for float_type in FLOAT_TYPES
    })
    sql_data_type_map.update({
        f'{json_type}[]': schema_ref('object') for json_type in JSON_TYPES
    })

    for array_type in ['bit', 'boolean', 'character varying', 'cidr', 'citext',
                       'date', 'inet', 'mac', 'money', 'time', 'uuid']:
        sql_data_type_map[f'{array_type}[]'] = schema_ref(array_type)

    if col_info.sql_data_type == 'numeric[]':
        scale = postgres.numeric_scale(col_info)
        precision = postgres.numeric_precision(col_info)
        schema_name = schema_name_for_numeric_array(precision, scale)
        column_schema['items'] = {'$ref': f'#/definitions/{schema_name}'}
    elif col_info.sql_data_type in sql_data_type_map:
        column_schema['items'] = {'$ref': sql_data_type_map[col_info.sql_data_type]}
    else:
        column_schema['items'] = {'$ref': schema_ref('string')}

    return column_schema


def nullable_columns(col_types, pk):
    return col_types if pk else ['null'] + col_types


def nullable_column(col_type, pk):
    return [col_type] if pk else ['null', col_type]


def schema_name_for_numeric_array(precision, scale):
    return f'sdc_recursive_decimal_{precision}_{scale}_array'


def include_array_schemas(columns, schema):
    schema['definitions'] = copy.deepcopy(BASE_RECURSIVE_SCHEMAS)

    decimal_array_columns = [key for key, value in columns.items() if value.sql_data_type == 'numeric[]']
    for col in decimal_array_columns:
        scale = postgres.numeric_scale(columns[col])
        precision = postgres.numeric_precision(columns[col])
        schema_name = schema_name_for_numeric_array(precision, scale)
        schema['definitions'][schema_name] = {'type': ['null', 'number', 'array'],
                                              'multipleOf': postgres.numeric_multiple_of(scale),
                                              'exclusiveMaximum': True,
                                              'maximum': postgres.numeric_max(precision, scale),
                                              'exclusiveMinimum': True,
                                              'minimum': postgres.numeric_min(precision, scale),
                                              'items': {'$ref': f'#/definitions/{schema_name}'}}

    return schema


def write_sql_data_type_md(mdata, col_info):
    c_name = col_info.column_name
    if col_info.sql_data_type == 'bit' and col_info.character_maximum_length > 1:
        mdata = metadata.write(mdata, ('properties', c_name),
                               'sql-datatype', f"bit({col_info.character_maximum_length})")
    else:
        mdata = metadata.write(mdata, ('properties', c_name), 'sql-datatype', col_info.sql_data_type)

    return mdata


def dump_catalog(all_streams: List[Dict]) -> None:
    """
    Prints the catalog of all streams to the standard output in a JSON format with an indentation of 2 spaces.
    Args:
        all_streams: List of streams to dump
    """
    json.dump({'streams': all_streams}, sys.stdout, indent=2)


def is_selected_via_metadata(stream: Dict) -> bool:
    """
    This function determines whether a given stream has been selected through its metadata.
    Args:
        stream: A dictionary representing the stream.

    Returns: A boolean value indicating if the stream is selected or not.
    """
    table_md = metadata.to_map(stream['metadata']).get((), {})
    return table_md.get('selected', False)


def clear_state_on_replication_change(state: Dict,
                                      tap_stream_id: str,
                                      replication_method: str) -> Dict:
    """
    Detects a change in the replication method and updates the state accordingly. Returns the new state dictionary.

    :param state: the current state dictionary
    :param tap_stream_id: the tap stream ID
    :param replication_method: the current replication method
    :return: a new state dictionary
    """
    last_replication_method = singer.get_bookmark(state, tap_stream_id, 'last_replication_method')
    if last_replication_method is not None and (replication_method != last_replication_method):
        state = singer.reset_stream(state, tap_stream_id)

    state = singer.write_bookmark(state, tap_stream_id, 'last_replication_method', replication_method)

    return state


def refresh_streams_schema(conn_config: Dict, streams: List[Dict]):
    """
    Refreshes the schema and metadata of given streams with new discovery.

    This function queries the database to discover new schema and metadata for the given streams
    and updates them in-place. The given `streams` list of dictionaries would be mutated and updated.

    Args:
        conn_config (Dict): A dictionary containing the database connection information.
        streams (List[Dict]): A list of stream dictionaries to be updated.

    Returns:
        None
    """

    with connect(conn_config) as conn:
        new_discovery = {
            stream['tap_stream_id']: stream
            for stream in discover_db(conn, conn_config.get('filter_schemas'), [st['table_name'] for st in streams])
        }

        LOGGER.debug('Found new schemas %s', new_discovery)

        # For every stream dictionary, update the schema and metadata from the new discovery
        for idx, stream in enumerate(streams):
            streams[idx]['schema'] = copy.deepcopy(new_discovery[stream['tap_stream_id']]['schema'])

            # Step 1: Preserve non-discoverable metadata from the original stream object.
            # Example: replication method is not present in the new discovery metadata.
            md_map = metadata.to_map(stream['metadata'])
            meta = md_map.get(())

            for idx_met, metadatum in enumerate(new_discovery[stream['tap_stream_id']]['metadata']):
                if not metadatum['breadcrumb']:
                    meta.update(new_discovery[stream['tap_stream_id']]['metadata'][idx_met]['metadata'])
                    new_discovery[stream['tap_stream_id']]['metadata'][idx_met]['metadata'] = meta

            # Step 2: Copy all metadata from the updated new discovery to the original stream.
            streams[idx]['metadata'] = copy.deepcopy(new_discovery[stream['tap_stream_id']]['metadata'])

    LOGGER.debug('Streams schemas updated with new schemas%s', streams)


def has_logical_streams(streams: list, replication_method: str) -> bool:
    """
    Determines if any stream in the given list has a replication method of LOG_BASED.

    Args:
        streams: A list of streams to check.
        replication_method: The replication method to check for.

    Returns:
        True if any stream has a replication method of LOG_BASED, False otherwise.
    """
    for stream in streams:
        stream_metadata = metadata.to_map(stream['metadata'])
        if stream_metadata.get((), {}).get('replication-method', replication_method) == 'LOG_BASED':
            return True

    return False
