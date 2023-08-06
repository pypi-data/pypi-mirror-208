import copy
import time
from functools import partial

import psycopg2
import psycopg2.extras
import singer
from singer import metrics
from singer import utils

import macrometa_source_postgres.connection as postgres

LOGGER = singer.get_logger('macrometa_source_postgres')


def sync_view(conn_info, stream, state, desired_columns, md_map):
    """
    Replicate a PostgreSQL view to target destination.

    :param dict conn_info: dictionary of connection parameters to connect to PostgreSQL
    :param dict stream: dictionary of stream metadata
    :param dict state: dictionary representing the state of the replication process
    :param list desired_columns: list of desired columns for the view
    :param dict md_map: dictionary mapping metadata to the relevant stream
    :return: updated state dictionary representing the state of the replication process
    """

    # Get the current time for time_extracted
    time_extracted = utils.now()

    # Get the current version of the stream, or generate a new one
    current_version = singer.get_bookmark(state, stream['tap_stream_id'], 'version')
    if current_version is None:
        current_version = int(time.time() * 1000)
        state = singer.write_bookmark(state, stream['tap_stream_id'], 'version', current_version)
        singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

    # Get the schema name from the metadata mapping
    schema_name = md_map.get(()).get('schema-name')

    # Prepare the column names for use in the SQL query
    escaped_columns = map(postgres.prepare_columns_sql, desired_columns)

    # Create an activate version message to use when sending records
    activate_version_message = singer.ActivateVersionMessage(
        stream=postgres.calculate_destination_stream_name(stream, md_map),
        version=current_version)

    with metrics.record_counter(None) as counter:
        # Open a connection to PostgreSQL and create a cursor
        with postgres.connect(conn_info) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor, name='macrometa_cursor') as cur:
                # Set the cursor's batch size to CURSOR_ITER_SIZE
                cur.itersize = postgres.CURSOR_ITER_SIZE
                
                # Construct the SQL SELECT statement to retrieve records from the view
                select_sql = f"SELECT {','.join(escaped_columns)} FROM " \
                             f"{postgres.fully_qualified_table_name(schema_name, stream['table_name'])}"

                LOGGER.info("Fetching rows with iterator size of %s for SQL query: '%s'", cur.itersize, select_sql)
                cur.execute(select_sql)

                # Iterate through the records returned by the query
                for rows_saved, rec in enumerate(cur, start=1):
                    # Convert the record to a Singer message and write it to the target
                    record_message = postgres.selected_row_to_singer_message(stream,
                                                                            rec,
                                                                            current_version,
                                                                            desired_columns,
                                                                            time_extracted,
                                                                            md_map)
                    singer.write_message(record_message)

                    # Update state and send a message every 1000 rows
                    if rows_saved % 1000 == 0:
                        singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

                    # Increment the counter for metrics recording
                    counter.increment()

    # Always send the activate version message after all records have been sent
    singer.write_message(activate_version_message)

    return state


def sync_table(conn_info, stream, state, desired_columns, md_map):
    """
    Replicate a PostgreSQL table to target destination.

    :param dict conn_info: dictionary of connection parameters to connect to PostgreSQL
    :param dict stream: dictionary of stream metadata
    :param dict state: dictionary representing the state of the replication process
    :param list desired_columns: list of desired columns for the table
    :param dict md_map: dictionary mapping metadata to the relevant stream
    :return: updated state dictionary representing the state of the replication process
    """
    time_extracted = utils.now()

    # check the version if it already exists
    first_run = singer.get_bookmark(state, stream['tap_stream_id'], 'version') is None

    # xmin indicates that we were interrupted last time
    if singer.get_bookmark(state, stream['tap_stream_id'], 'xmin') is None:
        nascent_stream_version = int(time.time() * 1000)
    else:
        nascent_stream_version = singer.get_bookmark(state, stream['tap_stream_id'], 'version')

    state = singer.write_bookmark(state,
                                  stream['tap_stream_id'],
                                  'version',
                                  nascent_stream_version)
    singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

    schema_name = md_map.get(()).get('schema-name')

    escaped_columns = map(partial(postgres.prepare_columns_for_select_sql, md_map=md_map), desired_columns)

    activate_version_message = singer.ActivateVersionMessage(
        stream=postgres.calculate_destination_stream_name(stream, md_map),
        version=nascent_stream_version)

    if first_run:
        singer.write_message(activate_version_message)

    hstore_available = postgres.hstore_available(conn_info)
    with metrics.record_counter(None) as counter:
        with postgres.connect(conn_info) as conn:
            with conn.cursor() as cur:
                cur.execute("show server_encoding")
                LOGGER.info("The current server encoding is: %s", cur.fetchone()[0])
                cur.execute("show client_encoding")
                LOGGER.info("The current client encoding is: %s", cur.fetchone()[0])

            if hstore_available:
                LOGGER.info("hstore is available")
                psycopg2.extras.register_hstore(conn)
            else:
                LOGGER.info("hstore is not available")

            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor, name='macrometa_cursor') as cur:
                cur.itersize = postgres.CURSOR_ITER_SIZE

                fq_table_name = postgres.fully_qualified_table_name(schema_name, stream['table_name'])
                if xmin := singer.get_bookmark(
                    state, stream['tap_stream_id'], 'xmin'
                ):
                    LOGGER.info("Resuming Full Table replication %s with the starting point at xmin %s",
                                nascent_stream_version, xmin)
                    select_sql = f"""
                        SELECT {','.join(escaped_columns)}, xmin::text::bigint
                        FROM {fq_table_name} where age(xmin::xid) <= age('{xmin}'::xid)
                        ORDER BY xmin::text ASC"""
                else:
                    LOGGER.info("Initiating new FULL_TABLE replication %s.", nascent_stream_version)
                    select_sql = f"""SELECT {','.join(escaped_columns)}, xmin::text::bigint
                                      FROM {fq_table_name}
                                     ORDER BY xmin::text ASC"""

                LOGGER.info("Fetching rows with iterator size of %s for SQL query: '%s'", cur.itersize, select_sql)
                cur.execute(select_sql)

                for rows_saved, rec in enumerate(cur, start=1):
                    xmin = rec['xmin']
                    rec = rec[:-1]
                    record_message = postgres.selected_row_to_singer_message(stream,
                                                                            rec,
                                                                            nascent_stream_version,
                                                                            desired_columns,
                                                                            time_extracted,
                                                                            md_map)
                    singer.write_message(record_message)
                    state = singer.write_bookmark(state, stream['tap_stream_id'], 'xmin', xmin)
                    if rows_saved % 1000 == 0:
                        singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

                    counter.increment()

    # clean up the xmin bookmark once full table replication is completed.
    state = singer.write_bookmark(state, stream['tap_stream_id'], 'xmin', None)

    # send the activate version message
    singer.write_message(activate_version_message)

    return state
