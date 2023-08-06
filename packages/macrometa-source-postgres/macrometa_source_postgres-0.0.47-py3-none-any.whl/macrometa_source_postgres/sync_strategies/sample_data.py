from functools import partial

import psycopg2
import psycopg2.extras
from singer import metadata

import macrometa_source_postgres.connection as postgres
from macrometa_source_postgres.sync_strategies.common import should_sync_column


def fetch_view(conn_info, stream, desired_columns, md_map, limit=10):
    schema_name = md_map.get(()).get('schema-name')
    escaped_columns = map(postgres.prepare_columns_sql, desired_columns)
    samples = []
    with postgres.connect(conn_info) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor, name='macrometa_cursor') as cur:
            cur.itersize = postgres.CURSOR_ITER_SIZE
            select_sql = f"SELECT {','.join(escaped_columns)} FROM " \
                         f"{postgres.fully_qualified_table_name(schema_name, stream['table_name'])} LIMIT {limit}"
            cur.execute(select_sql)
            for rec in cur:
                rec_msg = postgres.selected_row_to_singer_message(stream, rec, None, desired_columns, None, md_map)
                samples.append(rec_msg.record)
    return samples


def fetch_table(conn_info, stream, desired_columns, md_map, limit=10):
    schema_name = md_map.get(()).get('schema-name')
    escaped_columns = map(partial(postgres.prepare_columns_for_select_sql, md_map=md_map), desired_columns)
    samples = []
    with postgres.connect(conn_info) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor, name='macrometa_cursor') as cur:
            cur.itersize = postgres.CURSOR_ITER_SIZE
            fq_table_name = postgres.fully_qualified_table_name(schema_name, stream['table_name'])
            select_sql = f"""SELECT {','.join(escaped_columns)}, xmin::text::bigint
                              FROM {fq_table_name}
                             ORDER BY xmin::text ASC LIMIT {limit}"""
            cur.execute(select_sql)
            for rec in cur:
                rec = rec[:-1]
                rec_msg = postgres.selected_row_to_singer_message(stream, rec, None, desired_columns, None, md_map)
                samples.append(rec_msg.record)
    return samples


def fetch_samples(conn_config, stream):
    """
    Fetch samples for the stream.
    """
    md_map = metadata.to_map(stream['metadata'])
    conn_config['dbname'] = md_map.get(()).get('database-name')
    desired_columns = [c for c in stream['schema']['properties'].keys() if should_sync_column(md_map, c)]
    desired_columns.sort()
    if not desired_columns:
        # There are no columns selected for stream. So, skipping it.
        return []
    if md_map.get((), {}).get('is-view'):
        state = fetch_view(conn_config, stream, desired_columns, md_map)
    else:
        state = fetch_table(conn_config, stream, desired_columns, md_map)

    # Appending _ to keys for preserving values of reserved keys in source data
    reserved_keys = ['_key', '_id', '_rev']
    if md_map.get((), {}).get('table-key-properties'):
        key_properties = md_map.get((), {}).get('table-key-properties')
        if key_properties[0] == '_key':
                reserved_keys.remove('_key')
    columns = set(desired_columns)
    if any(key in columns for key in reserved_keys):
        for record in state:
            record = modify_reserved_keys(record, reserved_keys)

    return state


def modify_reserved_keys(record, reserved_keys):
    for reserved_key in reserved_keys:
        if record.get(reserved_key):
            new_key = f"_{reserved_key}"
            while True:
                if record.get(new_key):
                    new_key = f"_{new_key}"
                else:
                    break
            record[new_key] = record.pop(reserved_key)
    return record
