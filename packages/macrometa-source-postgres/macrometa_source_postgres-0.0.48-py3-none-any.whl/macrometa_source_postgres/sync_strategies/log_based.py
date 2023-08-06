import copy
import contextlib
import datetime
import decimal
import json
import re
import warnings
from functools import reduce
from select import select

import psycopg2
import pytz
import singer
from dateutil.parser import parse, UnknownTimezoneWarning, ParserError
from psycopg2 import sql
from singer import metadata, utils, get_bookmark

import macrometa_source_postgres.connection as postgres
import macrometa_source_postgres.sync_strategies.common as sync_common
from macrometa_source_postgres.helper import refresh_streams_schema

LOGGER = singer.get_logger('macrometa_source_postgres')

FALLBACK_DATETIME = '9999-12-31T23:59:59.999+00:00'
FALLBACK_DATE = '9999-12-31T00:00:00+00:00'


class ReplicationSlotNotFoundError(Exception):
    """Raise exception when replication slot is not found"""


class UnsupportedPayloadKindError(Exception):
    """Raise exception hen waljson payload is not insert, update nor delete"""


def get_pg_version(conn_info):
    with postgres.connect(conn_info, False, True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT setting::int AS version FROM pg_settings WHERE name='server_version_num'")
            version = cur.fetchone()[0]
    return version


def lsn_to_int(lsn):
    """
    Converts a PostgreSQL Log Sequence Number (LSN) string into an integer format.

    LSN is represented in the format of two hexadecimal numbers separated by a forward slash.
    This function takes an LSN string and converts it to an integer by combining the two hexadecimal
    numbers into a 64-bit integer in big-endian byte order.

    :param lsn: A PostgreSQL Log Sequence Number in string format.
    :return: An integer representation of the LSN.
    :rtype: int
    """

    if not lsn:
        return None

    file, index = lsn.split('/')
    return (int(file, 16) << 32) + int(index, 16)


def int_to_lsn(lsni):
    """
    Convert an integer to PostgreSQL Log Sequence Number (LSN) format.

    :param lsni: An integer representing the LSN
    :return: A string representing the LSN in PostgreSQL's hex format (e.g., '0/16D68B0')
    """

    if not lsni:
        return None

    # Convert the integer to binary
    lsn_binary = f'{lsni:b}'

    # The 'file' portion is the binary before the 32nd character, converted to hex
    file = (format(int(lsn_binary[:-32], 2), 'x')).upper() if len(lsn_binary) > 32 else '0'

    # The 'index' portion is the binary from the 32nd character onwards, converted to hex
    index = (format(int(lsn_binary[-32:], 2), 'x')).upper()

    return f"{file}/{index}"


def fetch_current_lsn(conn_config):
    version = get_pg_version(conn_config)
    # Make sure PostgreSQL version is 9.4 or higher BUG #15114
    if (version >= 110000) and (version < 110002):
        raise Exception('An upgrade to PostgreSQL minor version 11.2 is required.')
    if (version >= 100000) and (version < 100007):
        raise Exception('An upgrade to PostgreSQL minor version 10.7 is required.')
    if (version >= 90600) and (version < 90612):
        raise Exception('An upgrade to PostgreSQL minor version 9.6.12 is required.')
    if (version >= 90500) and (version < 90516):
        raise Exception('An upgrade to PostgreSQL minor version 9.5.16 is required.')
    if (version >= 90400) and (version < 90421):
        raise Exception('An upgrade to PostgreSQL minor version 9.4.21 is required.')
    if version < 90400:
        raise Exception('PostgreSQL versions below 9.4 do not support logical replication.')

    with postgres.connect(conn_config, False, True) as conn:
        with conn.cursor() as cur:
            # If the PostgreSQL version is 10 or higher, use pg_current_wal_lsn(); else use pg_current_xlog_location().
            if version >= 100000:
                cur.execute("SELECT pg_current_wal_lsn() AS current_lsn")
            else:
                cur.execute("SELECT pg_current_xlog_location() AS current_lsn")

            current_lsn = cur.fetchone()[0]
            return lsn_to_int(current_lsn)


def add_automatic_properties(stream, debug_lsn: bool = False):
    stream['schema']['properties']['_sdc_deleted_at'] = {'type': ['null', 'string'], 'format': 'date-time'}

    if debug_lsn:
        LOGGER.debug('debug_lsn is ON')
        stream['schema']['properties']['_sdc_lsn'] = {'type': ['null', 'string']}
    else:
        LOGGER.debug('debug_lsn is OFF')

    return stream


def get_stream_version(tap_stream_id, state):
    stream_version = singer.get_bookmark(state, tap_stream_id, 'version')

    if stream_version is None:
        raise Exception(f"version not found for log miner {tap_stream_id}")

    return stream_version


def tuples_to_map(accum, t):
    accum[t[0]] = t[1]
    return accum


def create_hstore_elem_query(elem):
    return sql.SQL("SELECT hstore_to_array({})").format(sql.Literal(elem))


def create_hstore_elem(conn_info, elem):
    with postgres.connect(conn_info, False, True) as conn:
        with conn.cursor() as cur:
            query = create_hstore_elem_query(elem)
            cur.execute(query)
            res = cur.fetchone()[0]
            return reduce(tuples_to_map, [res[i:i + 2] for i in range(0, len(res), 2)], {})


def create_array_elem(elem, sql_datatype, conn_info):
    if elem is None:
        return None

    cast_datatype_mapping = {
        'bit[]': 'boolean[]',
        'boolean[]': 'boolean[]',
        'character varying[]': 'character varying[]',
        'cidr[]': 'cidr[]',
        'citext[]': 'text[]',
        'date[]': 'text[]',
        'double precision[]': 'double precision[]',
        'hstore[]': 'text[]',
        'integer[]': 'integer[]',
        'inet[]': 'inet[]',
        'json[]': 'text[]',
        'jsonb[]': 'text[]',
        'macaddr[]': 'macaddr[]',
        'money[]': 'text[]',
        'numeric[]': 'text[]',
        'real[]': 'real[]',
        'smallint[]': 'smallint[]',
        'text[]': 'text[]',
        'time without time zone[]': 'text[]',
        'time with time zone[]': 'text[]',
        'timestamp with time zone[]': 'text[]',
        'timestamp without time zone[]': 'text[]',
        'uuid[]': 'text[]',
    }

    cast_datatype = cast_datatype_mapping.get(sql_datatype, 'text[]')

    with postgres.connect(conn_info, False, True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT %s::%s", (elem, cast_datatype))
            return cur.fetchone()[0]


def convert_value_to_singer_value(value, original_sql_datatype, conn_info):
    """
    Convert a database value to the Singer format based on the SQL datatype.
    
    :param value: The value to be converted
    :param original_sql_datatype: The original SQL datatype of the value
    :param conn_info: The connection information for the database
    :return: The converted value in Singer format
    """
    sql_datatype = original_sql_datatype.replace('[]', '')

    if value is None:
        return value

    if sql_datatype == 'money':
        return value

    if sql_datatype in ['json', 'jsonb']:
        return json.loads(value)

    if sql_datatype == 'timestamp without time zone':
        if isinstance(value, datetime.datetime):
            # if max datetime is passed return fallback date
            if value > datetime.datetime(9999, 12, 31, 23, 59, 59, 999000):
                return FALLBACK_DATETIME

            return f'{value.isoformat()}+00:00'

        with warnings.catch_warnings():
            #  Date with era (BC, AD) to be parsed as fallback date
            warnings.filterwarnings('error')
            try:
                parsed = parse(value)
                if parsed > datetime.datetime(9999, 12, 31, 23, 59, 59, 999000):
                    return FALLBACK_DATETIME

                return f'{parsed.isoformat()}+00:00'
            except (ParserError, UnknownTimezoneWarning):
                return FALLBACK_DATETIME

    if sql_datatype == 'timestamp with time zone':
        if isinstance(value, datetime.datetime):
            try:
                utc_datetime = value.astimezone(pytz.UTC).replace(tzinfo=None)
                if utc_datetime > datetime.datetime(9999, 12, 31, 23, 59, 59, 999000):
                    return FALLBACK_DATETIME

                return value.isoformat()
            except OverflowError:
                return FALLBACK_DATETIME

        with warnings.catch_warnings():
            #  Date with era (BC, AD) to be parsed as fallback date
            warnings.filterwarnings('error')
            try:
                parsed = parse(value)
                if parsed.astimezone(pytz.UTC).replace(tzinfo=None) > \
                        datetime.datetime(9999, 12, 31, 23, 59, 59, 999000):
                    return FALLBACK_DATETIME

                return parsed.isoformat()

            except (ParserError, UnknownTimezoneWarning, OverflowError):
                return FALLBACK_DATETIME

    if sql_datatype == 'date':
        if isinstance(value, datetime.date):
            # Date are usually string in Logbased replication unless they are from an array
            return f'{value.isoformat()}T00:00:00+00:00'
        try:
            return f"{parse(value).isoformat()}+00:00"
        except ValueError as e:
            match = re.match(r'year (\d+) is out of range', str(e))
            if match and int(match[1]) > 9999:
                LOGGER.warning('datetimes cannot handle years past 9999, returning %s for %s',
                               FALLBACK_DATE, value)
                return FALLBACK_DATE
            raise
    if sql_datatype == 'time with time zone':
        return extracted_time_zone_values(value, original_sql_datatype)
    if sql_datatype == 'time without time zone':
        if value.startswith('24'):
            value = value.replace('24', '00', 1)
        return parse(value).isoformat().split('T')[1]
    if sql_datatype == 'bit':
        # value = True for arrays
        # value = '1' for normal bits
        return value == '1' or value is True
    if sql_datatype == 'boolean':
        return value
    if sql_datatype == 'hstore':
        return create_hstore_elem(conn_info, value)
    if 'numeric' in sql_datatype:
        return decimal.Decimal(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, str):
        return value

    raise Exception(f"Failed to process value of type {type(value)}")


def extracted_time_zone_values(elem, original_sql_datatype):
    # Timezone values to be converted to UTC
    if elem.startswith('24'):
        elem = elem.replace('24', '00', 1)
    elem = f'{elem}00'
    elem_obj = datetime.datetime.strptime(elem, '%H:%M:%S%z')
    if elem_obj.utcoffset() != datetime.timedelta(seconds=0):
        LOGGER.warning('Values converted to UTC: %s', original_sql_datatype)
    elem_obj = elem_obj.astimezone(pytz.utc)
    elem = elem_obj.strftime('%H:%M:%S')
    return parse(elem).isoformat().split('T')[1]


def convert_array_to_singer_value(elem, sql_datatype, conn_info):
    if isinstance(elem, list):
        return list(map(lambda elem: convert_array_to_singer_value(elem, sql_datatype, conn_info), elem))

    return convert_value_to_singer_value(elem, sql_datatype, conn_info)


def convert_values_to_singer_values(elem, sql_datatype, conn_info):
    # Check if the given SQL datatype is an array
    if sql_datatype.find('[]') > 0:
        # If it's an array, convert each element to the appropriate Singer value
        cleaned_elem = create_array_elem(elem, sql_datatype, conn_info)
        return list(map(lambda elem: convert_array_to_singer_value(elem, sql_datatype, conn_info),
                        (cleaned_elem or [])))

    # If it's not an array, convert the value directly using the implementation function
    return convert_value_to_singer_value(elem, sql_datatype, conn_info)


def row_to_singer_message(stream, row, version, columns, time_extracted, md_map, conn_info):
    row_to_persist = ()
    md_map[('properties', '_sdc_deleted_at')] = {'sql-datatype': 'timestamp with time zone'}
    md_map[('properties', '_sdc_lsn')] = {'sql-datatype': "character varying"}

    for idx, elem in enumerate(row):
        sql_datatype = md_map.get(('properties', columns[idx])).get('sql-datatype')

        if not sql_datatype:
            LOGGER.info("No sql-datatype found for stream %s: %s", stream, columns[idx])
            raise Exception(f"Cannot determine sql-datatype for stream {stream}")

        cleaned_elem = convert_values_to_singer_values(elem, sql_datatype, conn_info)
        row_to_persist += (cleaned_elem,)

    rec = dict(zip(columns, row_to_persist))

    return singer.RecordMessage(
        stream=postgres.calculate_destination_stream_name(stream, md_map),
        record=rec,
        version=version,
        time_extracted=time_extracted)


def consume_message(streams, state, msg, time_extracted, conn_info):
    """
    Processes the given message and updates the state.

    :param streams: A list of streams with their metadata.
    :param state: The current state of the stream processing.
    :param msg: The message to be consumed, containing payload, data start, and other details.
    :param time_extracted: A datetime object representing when the data was extracted.
    :param conn_info: A dictionary containing connection information.

    :return: The updated state after processing the message.
    """
    try:
        payload = json.loads(msg.payload.lstrip(','))
    except Exception:
        return state

    lsn = msg.data_start
    streams_lookup = {s['tap_stream_id']: s for s in streams}
    tap_stream_id = postgres.compute_source_stream_id(payload['schema'], payload['table'])

    if (target_stream := streams_lookup.get(tap_stream_id)) is None:
        return state

    if payload['kind'] not in {'insert', 'update', 'delete'}:
        raise UnsupportedPayloadKindError(f"Invalid replication operation: {payload['kind']}")

    diff = set()
    if payload['kind'] in {'insert', 'update'}:
        diff = set(payload['columnnames']).difference(target_stream['schema']['properties'].keys())

    if diff:
        LOGGER.info('New columns detected "%s", refreshing schema of stream %s', diff, target_stream['stream'])
        refresh_streams_schema(conn_info, [target_stream])
        add_automatic_properties(target_stream, conn_info.get('debug_lsn', False))
        sync_common.send_schema_message(target_stream, ['lsn'])

    stream_version = get_stream_version(target_stream['tap_stream_id'], state)
    stream_md_map = metadata.to_map(target_stream['metadata'])
    desired_columns = {c for c in target_stream['schema']['properties'].keys() if sync_common.should_sync_column(stream_md_map, c)}


    column_data = []
    if payload['kind'] == 'delete':
        column_data = [(col, payload['oldkeys']['keyvalues'][idx]) for idx, col in enumerate(payload['oldkeys']['keynames']) if col in desired_columns]
        column_data.append(('_sdc_deleted_at', singer.utils.strftime(time_extracted)))
    else:
        column_data = [(col, payload['columnvalues'][idx]) for idx, col in enumerate(payload['columnnames']) if col in desired_columns]
        column_data.append(('_sdc_deleted_at', None))

    if conn_info.get('debug_lsn'):
        column_data.append(('_sdc_lsn', str(lsn)))

    col_names, col_vals = zip(*column_data)
    record_message = row_to_singer_message(target_stream,
                                           col_vals,
                                           stream_version,
                                           col_names,
                                           time_extracted,
                                           stream_md_map,
                                           conn_info)
    singer.write_message(record_message)
    state = singer.write_bookmark(state, target_stream['tap_stream_id'], 'lsn', lsn)

    return state


def generate_replication_slot_name(dbname, tap_id=None, prefix='macrometa'):
    """
    Generates a replication slot name based on the given parameters.
    
    :param dbname: str, the name of the database to be included in the replication slot name.
    :param tap_id: str, (optional) a unique identifier for the tap, to be appended to the slot name if provided.
    :param prefix: str, (optional) a prefix to be added to the replication slot name, defaults to 'macrometa'.
    
    :return: A well-formatted, lowercase replication slot name.
    :rtype: str
    """
    # If tap_id is provided, append it to the slot name with an underscore.
    tap_id_suffix = f'_{tap_id}' if tap_id else ''
    
    # Combine prefix, dbname, and tap_id_suffix to form the initial slot name.
    slot_name = f'{prefix}_{dbname}{tap_id_suffix}'.lower()

    # Replace any invalid characters in the slot name to comply with Postgres naming specifications.
    return re.sub('[^a-z0-9_]', '_', slot_name)


def locate_replication_slot_by_cur(cursor, dbname, replication_slot=None, tap_id=None):
    if replication_slot:
        # If replication slot is provided use that
        cursor.execute(f"SELECT * FROM pg_replication_slots WHERE slot_name = '{replication_slot}'")
        if len(cursor.fetchall()) == 1:
            LOGGER.info('Using replication slot %s from pg_replication_slots table.', replication_slot)
            return replication_slot
        raise ReplicationSlotNotFoundError(f'The replication slot {replication_slot} could not be found.')

    else:
        slot_name_v15 = generate_replication_slot_name(dbname)
        slot_name_v16 = generate_replication_slot_name(dbname, tap_id)

        # Ensure backward compatibility: first attempt to locate the existing v15 slot (for PPW <= 0.15.0).
        cursor.execute(f"SELECT * FROM pg_replication_slots WHERE slot_name = '{slot_name_v15}'")
        if len(cursor.fetchall()) == 1:
            LOGGER.info('Using replication slot %s from pg_replication_slots table.', slot_name_v15)
            return slot_name_v15

        # If the v15 replication slot is not found, attempt to locate the v16 replication slot.
        cursor.execute(f"SELECT * FROM pg_replication_slots WHERE slot_name = '{slot_name_v16}'")
        if len(cursor.fetchall()) == 1:
            LOGGER.info('Using replication slot %s from pg_replication_slots table.', slot_name_v16)
            return slot_name_v16

        raise ReplicationSlotNotFoundError(f'The replication slot {slot_name_v16} could not be found.')


def locate_replication_slot(conn_info):
    with postgres.connect(conn_info, False, True) as conn:
        with conn.cursor() as cur:
            return locate_replication_slot_by_cur(
                cur, conn_info['dbname'],
                conn_info['replication_slot'] if 'replication_slot' in conn_info else None,
                conn_info['tap_id'] if 'tap_id' in conn_info else None)


def streams_to_wal2json_tables(streams):
    """
    Create a comma-separated, escaped list of table names that can be used with the wal2json plugin.

    Given a list of Singer stream dictionaries, this function returns a string that can be used with the 'filter-tables'
    and 'add-tables' options of the wal2json plugin. The table names are case-sensitive, and any special characters
    (space, single quote, comma, period, asterisk) are escaped with a backslash. For example, the table "public"."Foo bar"
    should be specified as "public.Foo\ bar".

    :param streams: List of Singer stream dictionaries
    :return: tables (str): Comma-separated and escaped list of tables, compatible with the wal2json plugin
    :rtype: str
    """

    def escape_special_chars(string):
        escaped = string
        wal2json_special_chars = " ',.*"
        for ch in wal2json_special_chars:
            escaped = escaped.replace(ch, f'\\{ch}')
        return escaped

    tables = []
    for s in streams:
        schema_name = escape_special_chars(s['metadata'][0]['metadata']['schema-name'])
        table_name = escape_special_chars(s['table_name'])

        tables.append(f'{schema_name}.{table_name}')

    return ','.join(tables)


def sync_tables(conn_info, logical_streams, state, end_lsn, state_file):
    """
    Replicate PostgreSQL WAL logs for logical replication streams to target destination.

    :param dict conn_info: dictionary of connection parameters to connect to PostgreSQL
    :param list logical_streams: list of logical replication stream details
    :param dict state: dictionary representing the state of the replication process
    :param int end_lsn: ending LSN to stop replication
    :param str state_file: path to file containing state information
    :return: state dictionary representing the state of the replication process
    """

    # Initialize variables
    state_committed = state
    lsn_committed = min(
        [
            get_bookmark(state_committed, s['tap_stream_id'], 'lsn')
            for s in logical_streams
        ]
    )
    start_lsn = lsn_committed
    lsn_to_flush = None
    time_extracted = utils.now()
    slot = locate_replication_slot(conn_info)
    lsn_last_processed = None
    lsn_currently_processing = None
    lsn_processed_count = 0
    break_at_end_lsn = conn_info['break_at_end_lsn']
    poll_interval = 10
    poll_timestamp = None
    wal_sender_timeout = conn_info.get('wal_sender_timeout', 3600000)  # default 3600000 ms, i.e. 1 hour

    # Send schema message for each logical replication stream
    for s in logical_streams:
        sync_common.send_schema_message(s, ['lsn'])

    # Determine PostgreSQL version
    version = get_pg_version(conn_info)

    conn = postgres.connect(conn_info, True, True)
    cur = conn.cursor()

    # Adjust session wal_sender_timeout for PostgreSQL 12 and newer versions.
    if version >= 120000:
        LOGGER.info('Set the value of wal_sender_timeout session parameter to %i milliseconds.', wal_sender_timeout)
        cur.execute(f"SET SESSION wal_sender_timeout = {wal_sender_timeout}")

    # Start replication with logical replication stream
    try:
        LOGGER.info('Initiate streaming of Write-Ahead-Log (WAL) from %s up to %s using slot %s.',
                    int_to_lsn(start_lsn),
                    int_to_lsn(end_lsn),
                    slot)
        cur.start_replication(
            slot_name=slot,
            decode=True,
            start_lsn=start_lsn,
            status_interval=poll_interval,
            options={
                'write-in-chunks': 1,
                'add-tables': streams_to_wal2json_tables(logical_streams)
            }
        )

    except psycopg2.ProgrammingError as ex:
        raise Exception(f"Failed to initiate logical replication with the replication slot {ex}.") from ex

    # Initialize timestamp
    poll_timestamp = datetime.datetime.utcnow()

    try:
        while True:
            try:
                msg = cur.read_message()
            except Exception as e:
                LOGGER.error(e)
                raise

            if msg:
                if (break_at_end_lsn) and (msg.data_start > end_lsn):
                    LOGGER.info('The latest wal message %s is beyond the end_lsn %s, stopping replication.',
                                int_to_lsn(msg.data_start),
                                int_to_lsn(end_lsn))
                    break

                state = consume_message(logical_streams, state, msg, time_extracted, conn_info)

                # To ensure that we only flush to an LSN that has been entirely completed, when using wal2json
                # with the write-in-chunks option, multiple messages can have the same LSN.
                if lsn_currently_processing is None:
                    lsn_currently_processing = msg.data_start
                    LOGGER.info('The initial write-ahead log (WAL) message has been received: %s',
                                int_to_lsn(lsn_currently_processing))

                    # Flush Postgres WAL up to the last LSN committed in the previous run or up to 
                    # the first LSN received in this run.
                    lsn_to_flush = lsn_committed
                    if lsn_currently_processing < lsn_to_flush:
                        lsn_to_flush = lsn_currently_processing
                    LOGGER.info('Written up to %s, Flushing till the same %s',
                                int_to_lsn(lsn_to_flush),
                                int_to_lsn(lsn_to_flush))
                    cur.send_feedback(write_lsn=lsn_to_flush, flush_lsn=lsn_to_flush, reply=True, force=True)

                elif int(msg.data_start) > lsn_currently_processing:
                    lsn_last_processed = lsn_currently_processing
                    lsn_currently_processing = msg.data_start
                    lsn_processed_count = lsn_processed_count + 1
                    if lsn_processed_count >= 10000:
                        LOGGER.debug('Bookmarks for all streams are being updated to LSN = %s (%s)',
                                     lsn_last_processed,
                                     int_to_lsn(lsn_last_processed))
                        for s in logical_streams:
                            state = singer.write_bookmark(state, s['tap_stream_id'], 'lsn', lsn_last_processed)
                        singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))
                        lsn_processed_count = 0
            else:
                with contextlib.suppress(InterruptedError):
                     # Pause for one second if no message is received yet.
                     select([cur], [], [], 1)

            # Update the latest committed LSN position from the state file every poll_interval.
            if datetime.datetime.utcnow() >= poll_timestamp + datetime.timedelta(seconds=poll_interval):
                if lsn_currently_processing is None:
                    LOGGER.info('Awaiting the initial WAL (Write-Ahead Log) message.')
                else:
                    LOGGER.info('The most recent write-ahead log (WAL) message received was %s',
                                int_to_lsn(lsn_last_processed))
                    try:
                        with open(state_file, mode="r", encoding="utf-8") as fh:
                            state_committed = json.load(fh)
                    except Exception as e:
                        LOGGER.debug('Failed to open and parse json file %s: %s', state_file, e)
                    else:
                        lsn_committed = min(
                            [
                                get_bookmark(
                                    state_committed, s['tap_stream_id'], 'lsn'
                                )
                                for s in logical_streams
                            ]
                        )
                        if lsn_currently_processing > lsn_committed > lsn_to_flush:
                            lsn_to_flush = lsn_committed
                            LOGGER.info('Written up to %s, Flushing till the same %s',
                                        int_to_lsn(lsn_to_flush),
                                        int_to_lsn(lsn_to_flush))
                            cur.send_feedback(write_lsn=lsn_to_flush, flush_lsn=lsn_to_flush, reply=True, force=True)
                poll_timestamp = datetime.datetime.utcnow()

        cur.close()
        conn.close()
    finally:
        # Finally, updating bookmarks for all streams to the latest processed LSN.
        if lsn_last_processed:
            # If the last processed LSN is older than the committed LSN, then the last processed LSN is updated.
            if lsn_committed > lsn_last_processed:
                LOGGER.info('Updating current lsn_last_processed %s as it is older than lsn_committed %s',
                            int_to_lsn(lsn_last_processed),
                            int_to_lsn(lsn_committed))
                lsn_last_processed = lsn_committed

            LOGGER.info('Finally, updating bookmarks for all streams to the latest processed LSN = %s (%s)',
                        lsn_last_processed,
                        int_to_lsn(lsn_last_processed))

            for s in logical_streams:
                state = singer.write_bookmark(state, s['tap_stream_id'], 'lsn', lsn_last_processed)

        singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

    return state
