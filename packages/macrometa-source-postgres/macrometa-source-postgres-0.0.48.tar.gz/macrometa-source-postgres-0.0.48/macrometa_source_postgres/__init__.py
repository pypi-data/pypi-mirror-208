import argparse
import copy
import itertools

import pkg_resources
import psycopg2
import psycopg2.extensions
import psycopg2.extras
import singer
import singer.schema
import uuid
from c8connector import (
    C8Connector, ConfigProperty, Sample, Schema,
    ConfigAttributeType, SchemaAttributeType, SchemaAttribute)
from pathlib import Path
from singer import utils, metadata, get_bookmark
from singer.catalog import Catalog
from typing import Dict

import macrometa_source_postgres.connection as postgres
import macrometa_source_postgres.sync_strategies.common as sync_common
from macrometa_source_postgres.helper import (
    dump_catalog, clear_state_on_replication_change, discover_db,
    is_selected_via_metadata, refresh_streams_schema, has_logical_streams)
from macrometa_source_postgres.sync_strategies import full_table
from macrometa_source_postgres.sync_strategies import log_based
from macrometa_source_postgres.sync_strategies.sample_data import fetch_samples, modify_reserved_keys

LOGGER = singer.get_logger('macrometa_source_postgres')

REQUIRED_CONFIG_KEYS = [
    'dbname',
    'host',
    'port',
    'user',
    'password',
    'filter_schemas',
    'filter_table'
]


class PostgresSourceConnector(C8Connector):
    """PostgresSourceConnector's C8Connector impl."""

    def name(self) -> str:
        """Returns the name of the connector."""
        return "PostgreSQL"

    def package_name(self) -> str:
        """Returns the package name of the connector (i.e. PyPi package name)."""
        return "macrometa-source-postgres"

    def version(self) -> str:
        """Returns the version of the connector."""
        return pkg_resources.get_distribution('macrometa_source_postgres').version

    def type(self) -> str:
        """Returns the type of the connector."""
        return "source"

    def description(self) -> str:
        """Returns the description of the connector."""
        return "Source data from a PostgeSQL table."

    def logo(self) -> str:
        """Returns the logo image for the connector."""
        return ""

    def validate(self, integration: dict) -> None:
        """Validate given configurations against the connector.
        If invalid, throw an exception with the cause.
        """
        config = self.get_config(integration)
        try:
            config = create_certficate_files(config)
            do_discovery(config)
        except Exception as e:
            delete_certficate_files(config)
            raise e
        delete_certficate_files(config)

    def samples(self, integration: dict) -> list[Sample]:
        """Fetch sample data using the provided configurations."""
        config = self.get_config(integration)
        try:
            config = create_certficate_files(config)
            streams = do_discovery(config)
            results = []
            for stream in streams:
                s_attribs = []
                s_schema = stream['schema']

                data = fetch_samples(config, stream)[:10]
                # Appending _ to keys for preserving values of reserved keys in source data
                reserved_keys = ['_key', '_id', '_rev']
                if stream['metadata'][0]['metadata'].get('table-key-properties'):
                    key_properties = stream['metadata'][0]['metadata'].get('table-key-properties')
                    if key_properties[0] == '_key':
                            reserved_keys.remove('_key')
                s_schema['properties'] = modify_reserved_keys(s_schema['properties'], reserved_keys)

                for k, v in s_schema['properties'].items():
                    t = v['type'][-1]
                    s_attribs.append(SchemaAttribute(k, self.get_attribute_type(t)))
                schema = Schema(stream['stream'], s_attribs)
                results.append(Sample(
                    schema=schema,
                    data=data)
                )
        except Exception as e:
            LOGGER.info("Exception raised: %s", e)
            delete_certficate_files(config)
            raise e
        delete_certficate_files(config)
        return results

    def schemas(self, integration: dict) -> list[Schema]:
        """Get supported schemas using the given configurations."""
        config = self.get_config(integration)
        try:
            config = create_certficate_files(config)
            streams = do_discovery(config)
            results = []
            for stream in streams:
                s_attribs = []
                s_schema = stream['schema']

                # Appending _ to keys for preserving values of reserved keys in source data
                reserved_keys = ['_key', '_id', '_rev']
                if stream['metadata'][0]['metadata'].get('table-key-properties'):
                    key_properties = stream['metadata'][0]['metadata'].get('table-key-properties')
                    if key_properties[0] == '_key':
                            reserved_keys.remove('_key')
                s_schema['properties'] = modify_reserved_keys(s_schema['properties'], reserved_keys)

                for k, v in s_schema['properties'].items():
                    t = v['type'][-1]
                    s_attribs.append(SchemaAttribute(k, self.get_attribute_type(t)))
                results.append(Schema(stream['stream'], s_attribs))
        except Exception as e:
            LOGGER.info("Exception raised: %s", e)
            delete_certficate_files(config)
            raise e
        delete_certficate_files(config)
        return results

    def reserved_keys(self) -> list[str]:
        """List of reserved keys for the connector."""
        return []

    @staticmethod
    def get_attribute_type(source_type: str) -> SchemaAttributeType:
        if source_type == 'string':
            return SchemaAttributeType.STRING
        elif source_type == 'integer':
            return SchemaAttributeType.LONG
        elif source_type == 'boolean':
            return SchemaAttributeType.BOOLEAN
        elif source_type == 'number':
            return SchemaAttributeType.DOUBLE
        else:
            return SchemaAttributeType.OBJECT

    def config(self) -> list[ConfigProperty]:
        """Get configuration parameters for the connector."""
        return [
            ConfigProperty('host', 'Host', ConfigAttributeType.STRING, True, False,
                           description='PostgreSQL host.',
                           placeholder_value='postgres_host'),
            ConfigProperty('port', 'Port', ConfigAttributeType.INT, True, False,
                           description='PostgreSQL port.',
                           default_value='5432'),
            ConfigProperty('user', 'Username', ConfigAttributeType.STRING, True, False,
                           description='PostgreSQL user.',
                           default_value='postgres'),
            ConfigProperty('password', 'Password', ConfigAttributeType.PASSWORD, True, False,
                           description='PostgreSQL password.',
                           placeholder_value='password'),
            ConfigProperty('dbname', 'Database Name', ConfigAttributeType.STRING, True, False,
                           description='PostgreSQL database name.',
                           default_value='postgres'),
            ConfigProperty('filter_schemas', 'Source Schema', ConfigAttributeType.STRING, True, True,
                           description='Source Schema to scan.',
                           placeholder_value='my_schema'),
            ConfigProperty('filter_table', 'Source Table', ConfigAttributeType.STRING, True, True,
                           description='Source Table to scan.',
                           placeholder_value='my_table'),
            ConfigProperty('replication_method', 'Replication Method',
                           ConfigAttributeType.STRING, True, False,
                           description='Choose from LOG_BASED, FULL_TABLE.',
                           default_value='FULL_TABLE'),
            ConfigProperty('ssl', 'Use SSL', ConfigAttributeType.BOOLEAN, False, False,
                           description='If set to `true` then use SSL via postgres sslmode `require` option. '
			   	       'If the server does not accept SSL connections or the client certificate is not recognized'
			               ' then the connection will fail.',
                           default_value='false'),
            ConfigProperty('ssl_root_ca_cert', 'SSL CA Certificate', ConfigAttributeType.FILE, False, False,
                           description='Specific CA certificate in PEM string format. This is most often the case '
                                       'when using `self-signed` server certificate.',
                           placeholder_value="my_ca_certificate"),
            ConfigProperty('ssl_client_certificate', 'SSL Client Certificate', ConfigAttributeType.FILE, False, False,
                           description='Specific client certificate in PEM string format. The private key for client '
                                       'certificate should be specfied in a different parameter, SSL Client Key.',
                           placeholder_value="my_client_certificate"),
            ConfigProperty('ssl_client_key', 'SSL Client Key', ConfigAttributeType.FILE, False, False,
                           description='Specific client key in PEM string format.',
                           placeholder_value="my_client_key"),
            ConfigProperty('ssl_client_password', 'SSL Client Password', ConfigAttributeType.PASSWORD, False, False,
                           description='If the private key contained in the SSL Client Key is encrypted, users can provide a '
                                       'password or passphrase to decrypt the encrypted private keys.',
                           placeholder_value="my_client_password"),
            ConfigProperty('replication_slot', 'Replication Slot (LOG_BASED)', ConfigAttributeType.STRING, False, False,
                           description='PostgreSQL replication slot name required for LOG_BASED replication method.'
                                       ' This replication slot will be used to retrieve the required WAL files.'
                                       'If no value is provided replication slot is set as `macrometa_dbname` '
                                       '(dbname will be replaced by your database name).',
                           placeholder_value='macrometa_dbname'),
            ConfigProperty('break_at_end_lsn', 'Break at End LSN', ConfigAttributeType.BOOLEAN, False, False,
                           description='Stop running if the newly received LSN is after the max LSN that was initially'
                                       ' detected.',
                           default_value='false'),
            ConfigProperty('wal_sender_timeout', 'WAL Sender Timeout (milliseconds)', ConfigAttributeType.INT, False, False,
                           description='Terminate replication connections that are inactive for longer than this amount of time.'
                                       ' This is useful for the sending server to detect a standby crash or network outage.'
                                       ' Unit is milliseconds. The default value is 3600000 ms.',
                           default_value='3600000'),
            ConfigProperty('debug_lsn', 'Debug LSN', ConfigAttributeType.BOOLEAN, False, False,
                           description='If set to True then add _sdc_lsn property to the singer messages '
                                       'to debug postgres LSN position in the WAL stream.',
                           default_value='false'),
            ConfigProperty('itersize', 'Iterator Size', ConfigAttributeType.INT, False, False,
                           description='PG cursor size for FULL_TABLE.',
                           default_value='20000'),
            ConfigProperty('use_secondary', 'Use Secondary', ConfigAttributeType.BOOLEAN, False, False,
                           description='Use a database replica for FULL_TABLE replication.',
                           default_value='false'),
            ConfigProperty('secondary_host', 'Secondary Host', ConfigAttributeType.STRING, False, False,
                           description='Required when using a secondary replica.',
                           placeholder_value='secondary_postgres_host'),
            ConfigProperty('secondary_port', 'Secondary Port', ConfigAttributeType.INT, False, False,
                           description='Required when using a secondary replica.',
                           placeholder_value='5432')
        ]

    def capabilities(self) -> list[str]:
        """Return the capabilities[1] of the connector.
        [1] https://docs.meltano.com/contribute/plugins#how-to-test-a-tap
        """
        return ['catalog', 'discover', 'state']

    @staticmethod
    def get_config(integration: dict) -> dict:
        try:
            return {
                # Required config keys
                'host': integration['host'],
                'user': integration['user'],
                'password': integration['password'],
                'port': integration['port'],
                'dbname': integration['dbname'],
                'filter_schemas': integration['filter_schemas'],
                'filter_table': integration['filter_table'],
                # Optional config keys
                'ssl': integration.get('ssl', False),
                'ssl_root_ca_cert': integration.get('ssl_root_ca_cert'),
                'ssl_client_certificate': integration.get('ssl_client_certificate'),
                'ssl_client_key': integration.get('ssl_client_key'),
                'ssl_client_password': integration.get('ssl_client_password'),
                'tap_id': integration.get('tap_id'),
                'replication_slot': integration.get('replication_slot'),
                'debug_lsn': integration.get('debug_lsn', False),
                'wal_sender_timeout': integration.get('wal_sender_timeout', 3600000),
                'break_at_end_lsn': integration.get('break_at_end_lsn', True),
                'use_secondary': integration.get('use_secondary', False),
            }
        except KeyError as e:
            raise KeyError(f'Integration property `{e}` not found.') from e


def do_discovery(conn_config):
    """
    Find all potential streams in the database cluster using discovery mode.

    Args:
        conn_config: A dictionary containing the configuration parameters for the database connection.

    Returns:
        A list of dictionaries representing the discovered streams.

    Raises:
        RuntimeError: If no tables were discovered across the entire cluster.
    """
    with postgres.connect(conn_config) as conn:
        LOGGER.info("Discovery started for db %s", conn_config['dbname'])
        filter_table = conn_config.get('filter_table')
        streams = discover_db(conn, conn_config.get('filter_schemas'),
                              [filter_table] if filter_table is not None else None)

    if len(streams) == 0:
        raise RuntimeError('No tables were discovered')

    dump_catalog(streams)
    return streams


def do_sync_full_table(conn_config, stream, state, desired_columns, md_map):
    """
    Runs full table sync
    """
    LOGGER.info("Stream %s is using full_table replication", stream['tap_stream_id'])
    sync_common.send_schema_message(stream, [])
    if md_map.get((), {}).get('is-view'):
        state = full_table.sync_view(conn_config, stream, state, desired_columns, md_map)
    else:
        state = full_table.sync_table(conn_config, stream, state, desired_columns, md_map)
    return state


def sync_method_for_streams(streams, state, replication_method):
    """
    Determines the replication method of each stream based on its metadata and state.

    Args:
        streams: A list of streams to synchronize.
        state: The current state of the synchronization process.
        replication_method: The default replication method to use if not specified in stream metadata.

    Returns:
        A tuple containing the stream lookup, traditional streams, and logical streams.
    """
    # Initialize empty dictionaries and lists to keep track of discovered streams
    lookup = {}
    traditional_steams = []
    logical_streams = []

    # For each stream in the list, determine its replication method, clear its state if necessary, and update
    # the corresponding dictionary and list
    for stream in streams:
        # Get the replication method for the stream from its metadata, or use the default replication method
        stream_metadata = metadata.to_map(stream['metadata'])
        replication_method = stream_metadata.get((), {}).get('replication-method', replication_method)

        state = clear_state_on_replication_change(state, stream['tap_stream_id'], replication_method)

        if replication_method not in {'LOG_BASED', 'FULL_TABLE'}:
            raise Exception(f"Invalid Replication method '{replication_method}'. "
                            f"Please use either 'FULL_TABLE' or 'LOG_BASED'.")

        # Get the desired columns for the stream based on its metadata
        md_map = metadata.to_map(stream['metadata'])
        desired_columns = [c for c in stream['schema']['properties'].keys() if
                           sync_common.should_sync_column(md_map, c)]
        desired_columns.sort()

        if not desired_columns:
            LOGGER.warning('No columns selected for stream %s, skipping it', stream['tap_stream_id'])
            continue

        if replication_method == 'LOG_BASED' and stream_metadata.get((), {}).get('is-view'):
            raise Exception(f'LogBased Replication is NOT supported for views. '
                            f'FULL_TABLE replication method should be used for {stream["tap_stream_id"]}')

        if replication_method == 'FULL_TABLE':
            lookup[stream['tap_stream_id']] = 'full'
            traditional_steams.append(stream)
        elif get_bookmark(state, stream['tap_stream_id'], 'xmin') and \
                get_bookmark(state, stream['tap_stream_id'], 'lsn'):
            # Let's finish the interrupted full-table replication.
            lookup[stream['tap_stream_id']] = 'logical_initial_interrupted'
            traditional_steams.append(stream)

        # Inconsistent state
        elif get_bookmark(state, stream['tap_stream_id'], 'xmin') and \
                not get_bookmark(state, stream['tap_stream_id'], 'lsn'):
            raise Exception("Xmin found(%s) in state but lsn is not present.")

        elif not get_bookmark(state, stream['tap_stream_id'], 'xmin') and \
                not get_bookmark(state, stream['tap_stream_id'], 'lsn'):
            # First we do a full_table replucation followed by log_based
            lookup[stream['tap_stream_id']] = 'logical_initial'
            traditional_steams.append(stream)

        else:
            # Full_table has been completed. Now moving to pure log_based replication
            lookup[stream['tap_stream_id']] = 'pure_logical'
            logical_streams.append(stream)

    return lookup, traditional_steams, logical_streams


def sync_traditional_stream(conn_config, stream, state, sync_method, end_lsn):
    """
    Syncs data from a PostgreSQL table for streams with FULL_TABLE replication. 
    
    Args:
        conn_config (dict): A dictionary containing database connection details.
        stream (dict): A dictionary containing metadata about the PostgreSQL table.
        state (dict): A dictionary containing the state of the current sync.
        sync_method (str): The sync method to use ('full', 'logical_initial', 'logical_initial_interrupted').
        end_lsn (int): The end LSN (Log Sequence Number) for the stream.

    Returns:
        dict: The updated state after the sync.
    """
    LOGGER.info("Beginning sync of stream(%s) with sync method(%s)", stream['tap_stream_id'], sync_method)
    md_map = metadata.to_map(stream['metadata'])
    conn_config['dbname'] = md_map.get(()).get('database-name')
    desired_columns = [c for c in stream['schema']['properties'].keys() if sync_common.should_sync_column(md_map, c)]
    desired_columns.sort()

    if not desired_columns:
        LOGGER.warning('There are no columns selected for stream %s, skipping it', stream['tap_stream_id'])
        return state

    register_type_adapters(conn_config)

    if sync_method == 'full':
        state = singer.set_currently_syncing(state, stream['tap_stream_id'])
        state = do_sync_full_table(conn_config, stream, state, desired_columns, md_map)
    elif sync_method == 'logical_initial':
        state = singer.set_currently_syncing(state, stream['tap_stream_id'])
        LOGGER.info("Syncing Full table first")
        state = singer.write_bookmark(state, stream['tap_stream_id'], 'lsn', end_lsn)

        sync_common.send_schema_message(stream, [])
        state = full_table.sync_table(conn_config, stream, state, desired_columns, md_map)
        state = singer.write_bookmark(state, stream['tap_stream_id'], 'xmin', None)
    elif sync_method == 'logical_initial_interrupted':
        state = singer.set_currently_syncing(state, stream['tap_stream_id'])
        LOGGER.info("Full table sync interrupted. Resuming it...")
        sync_common.send_schema_message(stream, [])
        state = full_table.sync_table(conn_config, stream, state, desired_columns, md_map)
    else:
        raise Exception(f"Invalid sync method {sync_method} for stream {stream['tap_stream_id']}")

    state = singer.set_currently_syncing(state, None)
    singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))
    return state


def sync_logical_streams(conn_config, logical_streams, state, end_lsn, state_file):
    """
    Syncs data from a PostgreSQL table for streams with LOG_BASED replication. 
    

    Args:
        conn_config (dict): A dictionary containing the database connection details.
        logical_streams (List[dict]): A list of dictionaries containing metadata about the PostgreSQL tables to sync.
        state (dict): A dictionary containing the current state of the sync.
        end_lsn (int): The LSN (Log Sequence Number) for the end of the replication stream.
        state_file (str): The name of the file to write the state to.

    Returns:
        dict: The updated state after the sync.
    """
    if logical_streams:
        LOGGER.info("Pure Logical Replication upto lsn %s for (%s)", end_lsn,
                    [s['tap_stream_id'] for s in logical_streams])

        logical_streams = [log_based.add_automatic_properties(
            s, conn_config.get('debug_lsn', False)) for s in logical_streams]

        selected_streams = {stream['tap_stream_id'] for stream in logical_streams}
        new_state = dict(currently_syncing=state['currently_syncing'], bookmarks={})

        for stream, bookmark in state['bookmarks'].items():
            if bookmark == {} or bookmark['last_replication_method'] != 'LOG_BASED' or stream in selected_streams:
                new_state['bookmarks'][stream] = bookmark
        state = new_state

        state = log_based.sync_tables(conn_config, logical_streams, state, end_lsn, state_file)

    return state


def register_type_adapters(conn_config):
    """
    Registers type adapters for custom and non-standard PostgreSQL data types.

    This function registers type adapters for handling non-standard PostgreSQL data types, such as arrays
    of citext, bit, UUID, and money types, as well as json, jsonb, and enum types. These adapters enable
    psycopg2 to correctly process and represent these data types when working with the database.

    :param conn_config: A dictionary containing the database connection configuration.
    """
    with postgres.connect(conn_config) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            register_array_type(cur, 'citext', 'CITEXT')
            register_array_type(cur, 'bit', 'BIT')
            register_array_type(cur, 'uuid', 'UUID')
            register_array_type(cur, 'money', 'MONEY')

            psycopg2.extras.register_default_json(loads=lambda x: str(x))
            psycopg2.extras.register_default_jsonb(loads=lambda x: str(x))

            cur.execute("SELECT distinct(t.typarray) FROM pg_type t JOIN pg_enum e ON t.oid = e.enumtypid")
            for oid in cur.fetchall():
                enum_oid = oid[0]
                psycopg2.extensions.register_type(
                    psycopg2.extensions.new_array_type(
                        (enum_oid,), f'ENUM_{enum_oid}[]', psycopg2.STRING))


def register_array_type(cur, typname, type_name):
    cur.execute(f"SELECT typarray FROM pg_type WHERE typname = '{typname}'")
    if array_oid := cur.fetchone():
        psycopg2.extensions.register_type(
            psycopg2.extensions.new_array_type(
                (array_oid[0],), f'{type_name}[]', psycopg2.STRING
            )
        )


def do_sync(conn_config, catalog, replication_method, state, state_file=None):
    """
    This function orchestrates the synchronization of all selected streams.
    Args:
        conn_config: Configuration object containing database connection details.
        catalog: Catalog of all streams in the database cluster.
        replication_method: Replication method to be used for synchronization.
        state: State of the last synchronization operation.
        state_file: Path to the state file.

     Returns:
        Updated state after completion of synchronization.
    """
    currently_syncing = singer.get_currently_syncing(state)
    streams = list(filter(is_selected_via_metadata, catalog['streams']))
    streams.sort(key=lambda s: s['tap_stream_id'])
    LOGGER.info("Streams: %s ", [s['tap_stream_id'] for s in streams])
    if has_logical_streams(streams, replication_method):
        # Need to fetch lsn for log_based replication
        end_lsn = log_based.fetch_current_lsn(conn_config)
    else:
        end_lsn = None

    refresh_streams_schema(conn_config, streams)

    sync_method_lookup, traditional_streams, logical_streams = \
        sync_method_for_streams(streams, state, replication_method)

    LOGGER.info(f"Logical streams previously: {logical_streams}")

    if currently_syncing:
        LOGGER.debug("Streams currently syncing are: %s", currently_syncing)

        currently_syncing_stream = list(filter(lambda s: s['tap_stream_id'] == currently_syncing, traditional_streams))

        if not currently_syncing_stream:
            LOGGER.warning("Currently syncing streams (%s) not found amongst the selected traditional streams(%s). "
                           "Ignoring them..",
                           currently_syncing,
                           {s['tap_stream_id'] for s in traditional_streams})

        other_streams = list(filter(lambda s: s['tap_stream_id'] != currently_syncing, traditional_streams))
        traditional_streams = currently_syncing_stream + other_streams
    else:
        LOGGER.info("None of the streams are marked as currently syncing in state file.")

    for stream in traditional_streams:
        state = sync_traditional_stream(conn_config,
                                        stream,
                                        state,
                                        sync_method_lookup[stream['tap_stream_id']],
                                        end_lsn)

    _, _, logical_streams = sync_method_for_streams(streams, state, replication_method)

    LOGGER.info(f"Logical streams now: {logical_streams}")

    logical_streams.sort(key=lambda s: metadata.to_map(s['metadata']).get(()).get('database-name'))
    for dbname, streams in itertools.groupby(logical_streams,
                                             lambda s: metadata.to_map(s['metadata']).get(()).get('database-name')):
        conn_config['dbname'] = dbname
        state = sync_logical_streams(conn_config, list(streams), state, end_lsn, state_file)
    return state


def create_certficate_files(config: Dict) -> Dict:
    path_uuid = uuid.uuid4().hex
    try:
        if config.get('ssl_root_ca_cert'):
            path = f"/opt/postgresql/{path_uuid}/ca.crt"
            ca_cert = Path(path)
            ca_cert.parent.mkdir(exist_ok=True, parents=True)
            ca_cert.write_text(create_ssl_string(config['ssl_root_ca_cert']))
            ca_cert.chmod(0o600)
            config['ssl_root_ca_cert'] = path
            LOGGER.info(f"CA certificate file created at: {path}")

        if config.get('ssl_client_certificate'):
            path = f"/opt/postgresql/{path_uuid}/client.crt"
            client_cert = Path(path)
            client_cert.parent.mkdir(exist_ok=True, parents=True)
            client_cert.write_text(create_ssl_string(config['ssl_client_certificate']))
            client_cert.chmod(0o600)
            config['ssl_client_certificate'] = path
            LOGGER.info(f"Client certificate file created at: {path}")

        if config.get('ssl_client_key'):
            path = f"/opt/postgresql/{path_uuid}/client.key"
            client_cert = Path(path)
            client_cert.parent.mkdir(exist_ok=True, parents=True)
            client_cert.write_text(create_ssl_string(config['ssl_client_key']))
            client_cert.chmod(0o600)
            config['ssl_client_key'] = path
            LOGGER.info(f"Client key file created at: {path}")
    except Exception as e:
        LOGGER.warn(f"Failed to create certificate: /opt/postgresql/{path_uuid}/. {e}")
    return config


def delete_certficate_files(config: Dict) -> None:
    try:
        cert = None
        if config.get('ssl_root_ca_cert'):
            path = config['ssl_root_ca_cert']
            cert = Path(path)
            config['ssl_root_ca_cert'] = cert.read_text()
            cert.unlink()
            LOGGER.info(f"CA certificate file deleted from: {path}")

        if config.get('ssl_client_certificate'):
            path = config['ssl_client_certificate']
            cert = Path(path)
            config['ssl_client_certificate'] = cert.read_text()
            cert.unlink()
            LOGGER.info(f"Client certificate file deleted from: {path}")

        if config.get('ssl_client_key'):
            path = config['ssl_client_key']
            cert = Path(path)
            config['ssl_client_key'] = cert.read_text()
            cert.unlink()
            LOGGER.info(f"Client key file deleted from: {path}")

        if cert is not None:
            cert.parent.rmdir()
    except Exception as e:
        LOGGER.warn(f"Failed to delete certificate: {e}")


def create_ssl_string(ssl_string: str) -> str:
    tls_certificate_key_list = []
    split_string = ssl_string.split("-----")
    if len(split_string) < 4:
        raise Exception("Invalid PEM format for certificate.")
    for i in range(len(split_string)):
        if ((i % 2) == 1):
            tls_certificate_key_list.extend(("-----", split_string[i], "-----"))
        else:
            tls_certificate_key_list.append(split_string[i].replace(' ', '\n'))

    return ''.join(tls_certificate_key_list)


def parse_args(required_config_keys):
    """Parses the command-line arguments and loads the JSON files

    Parses the command-line arguments which include -c, --config, -s, --state, -d, --discover, -p, --properties,
    --catalog. JSON files related to these arguments are loaded and parsed automatically.

    Args:
        required_config_keys (list): A list of required configuration keys

    Returns:
        argparse.Namespace: The parsed args object from argparse

    Raises:
        Exception: If the provided configuration key is not found
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config',
        help='Config file',
        required=True)

    parser.add_argument(
        '-s', '--state',
        help='state file')

    parser.add_argument(
        '-p', '--properties',
        help='Property selections: DEPRECATED, Please use --catalog instead')

    parser.add_argument(
        '--catalog',
        help='Catalog file')

    parser.add_argument(
        '-d', '--discover',
        action='store_true',
        help='Do schema discovery')

    args = parser.parse_args()
    if args.config:
        setattr(args, 'config_path', args.config)
        args.config = utils.load_json(args.config)
    if args.state:
        setattr(args, 'state_path', args.state)
        args.state_file = args.state
        args.state = utils.load_json(args.state)
    else:
        args.state_file = None
        args.state = {}
    if args.properties:
        setattr(args, 'properties_path', args.properties)
        args.properties = utils.load_json(args.properties)
    if args.catalog:
        setattr(args, 'catalog_path', args.catalog)
        args.catalog = Catalog.load(args.catalog)

    utils.check_config(args.config, required_config_keys)

    return args


def main_impl():
    """
    Main method
    """
    args = parse_args(REQUIRED_CONFIG_KEYS)
    conn_config = {
        # Required config keys
        'host': args.config['host'],
        'user': args.config['user'],
        'password': args.config['password'],
        'port': args.config['port'],
        'dbname': args.config['dbname'],
        'filter_schemas': args.config['filter_schemas'],
        'filter_table': args.config['filter_table'],

        # Optional config keys
        'ssl': args.config.get('ssl', False),
        'ssl_root_ca_cert': args.config.get('ssl_root_ca_cert'),
        'ssl_client_certificate': args.config.get('ssl_client_certificate'),
        'ssl_client_key': args.config.get('ssl_client_key'),
        'ssl_client_password': args.config.get('ssl_client_password'),
        'tap_id': args.config.get('tap_id'),
        'replication_slot': args.config.get('replication_slot'),
        'debug_lsn': args.config.get('debug_lsn', False),
        'wal_sender_timeout': args.config.get('wal_sender_timeout', 3600000),
        'break_at_end_lsn': args.config.get('break_at_end_lsn', True),
        'use_secondary': args.config.get('use_secondary', False),
    }

    if conn_config['use_secondary']:
        try:
            conn_config |= {
                # Secondary Host and Port are mandatory to use secondary connection.
                'secondary_host': args.config['secondary_host'],
                'secondary_port': args.config['secondary_port'],
            }
        except KeyError as exc:
            raise ValueError(
                "Use secondary is enabled but 'Secondary host' and 'Secondary port' are not defined."
            ) from exc

    try:
        conn_config = create_certficate_files(conn_config)

        postgres.CURSOR_ITER_SIZE = int(args.config.get('itersize', postgres.CURSOR_ITER_SIZE))

        if args.discover:
            do_discovery(conn_config)
        elif args.properties or args.catalog:
            state = args.state
            state_file = args.state_file
            do_sync(conn_config, args.catalog.to_dict() if args.catalog else args.properties,
                    args.config.get('replication_method'), state, state_file)
        else:
            LOGGER.info("No properties were selected")
    except Exception as e:
        LOGGER.info("Exception raised: %s", e)
        delete_certficate_files(conn_config)
        raise e
    delete_certficate_files(conn_config)


def main():
    """
    main
    """
    try:
        main_impl()
    except Exception as exc:
        LOGGER.critical(exc)
        raise exc
