#!/usr/bin/env python3
import copy
import json
import sys
from typing import List, Dict

import pkg_resources
import singer
from pymongo import MongoClient
from singer import metadata, metrics, utils
from c8connector import (
    C8Connector, ConfigProperty, Sample, Schema,
    ConfigAttributeType, SchemaAttribute)

from macrometa_source_mongo.sync_strategies import log_based
from macrometa_source_mongo.sync_strategies import common
from macrometa_source_mongo.sync_strategies import full_table
from macrometa_source_mongo.sync_strategies.sample_data import fetch_samples
from macrometa_source_mongo.connection import create_certficate_files, delete_certficate_files, \
    get_connection_string, get_user_databases
from macrometa_source_mongo.exceptions import InvalidReplicationMethodException, NoReadPrivilegeException
from macrometa_source_mongo.helper import filter_streams_by_replication_method, get_attribute_type, \
    get_streams_to_sync, produce_collection_schema, streams_list_to_dict, \
    write_schema_message

LOGGER = singer.get_logger('macrometa_source_mongo')

REQUIRED_CONFIG_KEYS = [
    'host',
    'user',
    'password',
    'auth_database',
    'database',
    'source_collection',
    'replication_method'
]

REQUIRED_CONFIG_KEYS_NON_SRV = REQUIRED_CONFIG_KEYS + ['port']

LOG_BASED_METHOD = 'LOG_BASED'
FULL_TABLE_METHOD = 'FULL_TABLE'


class MongoSourceConnector(C8Connector):
    """MongoSourceConnector's C8Connector impl."""

    def name(self) -> str:
        """Returns the name of the connector."""
        return "MongoDB"

    def package_name(self) -> str:
        """Returns the package name of the connector (i.e. PyPi package name)."""
        return "macrometa-source-mongo"

    def version(self) -> str:
        """Returns the version of the connector."""
        return pkg_resources.get_distribution('macrometa_source_mongo').version

    def type(self) -> str:
        """Returns the type of the connector."""
        return "source"

    def description(self) -> str:
        """Returns the description of the connector."""
        return "Source data from a MongoDB collection."

    def validate(self, integration: dict) -> None:
        """Validate given configurations against the connector.
        If invalid, throw an exception with the cause.
        """
        config = self.get_config(integration)
        try:
            config = create_certficate_files(config)
            client = self.get_client(config)
            do_discover(client, config)
        except Exception as e:
            delete_certficate_files(config)
            raise e
        delete_certficate_files(config)

    def samples(self, integration: dict) -> list[Sample]:
        """Fetch sample data using the provided configurations."""
        config = self.get_config(integration)
        try:
            config = create_certficate_files(config)
            client = self.get_client(config)
            streams = do_discover(client, config)
            results = []
            for stream in streams:
                schema, data = fetch_samples(client, config, stream)
                # Appending _ to keys inorder for preserving values of reserved keys in source data
                schema['__id'] = schema.pop('_id')
                data = data[:10]
                for record in data:
                    record['__id'] = record.pop('_id')
                results.append(Sample(
                    schema=Schema(stream["table_name"],
                                  [SchemaAttribute(k, get_attribute_type(v)) for k, v in schema.items()]),
                    data=data
                ))
        except Exception as e:
            delete_certficate_files(config)
            raise e
        delete_certficate_files(config)
        return results

    def schemas(self, integration: dict) -> list[Schema]:
        """Get supported schemas using the given configurations."""
        config = self.get_config(integration)
        try:
            config = create_certficate_files(config)
            client = self.get_client(config)
            streams = do_discover(client, config)
            results = []
            for stream in streams:
                schema, _ = fetch_samples(client, config, stream)
                # Appending _ to keys inorder for preserving values of reserved keys in source data
                schema['__id'] = schema.pop('_id')
                results.append(Schema(stream["table_name"],
                                      [SchemaAttribute(k, get_attribute_type(v)) for k, v in schema.items()]))
        except Exception as e:
            delete_certficate_files(config)
            raise e
        delete_certficate_files(config)
        return results

    def logo(self) -> str:
        """Returns the logo image for the connector."""
        return ""

    def reserved_keys(self) -> list[str]:
        """List of reserved keys for the connector."""
        return []

    def config(self) -> list[ConfigProperty]:
        """Get configuration parameters for the connector."""
        return [
            ConfigProperty('host', 'Host', ConfigAttributeType.STRING, True, False,
                           description='MongoDB host.',
                           placeholder_value='mongodb_host'),
            ConfigProperty('port', 'Port', ConfigAttributeType.INT, False, False,
                           description='MongoDB port.',
                           default_value='27017'),
            ConfigProperty('user', 'Username', ConfigAttributeType.STRING, True, False,
                           description='MongoDB user.',
                           placeholder_value='mongo'),
            ConfigProperty('password', 'Password', ConfigAttributeType.PASSWORD, True, False,
                           description='MongoDB password.',
                           placeholder_value='password'),
            ConfigProperty('auth_database', 'Auth Database', ConfigAttributeType.STRING, True, False,
                           description='MongoDB authentication database.',
                           default_value='admin'),
            ConfigProperty('database', 'Database', ConfigAttributeType.STRING, True, True,
                           description='MongoDB database name.',
                           placeholder_value='mongo'),
            ConfigProperty('source_collection', 'Source Collection', ConfigAttributeType.STRING, True, True,
                           description="Source collection name.", placeholder_value="my_collection"),
            ConfigProperty('replication_method', 'Replication Method', ConfigAttributeType.STRING, False, False,
                           description='Choose from LOG_BASED, FULL_TABLE.',
                           default_value='FULL_TABLE'),
            ConfigProperty('srv', 'Enable SRV', ConfigAttributeType.BOOLEAN, False, False,
                           description='Uses a `mongodb+srv` protocol to connect. Disables the usage of `port` '
                                       'argument if set to `True`.',
                           default_value="false"),
            ConfigProperty('replica_set', 'Replica Set', ConfigAttributeType.STRING, False, False,
                           description='Name of replica set.',
                           placeholder_value='replica'),
            ConfigProperty('ssl', 'Use SSL', ConfigAttributeType.BOOLEAN, False, False,
                           description='Can be set to true to connect using SSL.',
                           default_value="false"),
            ConfigProperty('verify_mode', 'Verify Mode', ConfigAttributeType.BOOLEAN, False, False,
                           description='Default SSL verify mode.',
                           default_value="true"),
            ConfigProperty('direct_connection', 'Direct Connection', ConfigAttributeType.BOOLEAN, False, False,
                           description='Specifies whether to connect directly to the specified MongoDB host as a '
                                       'standalone or connect to the entire replica set of which the given MongoDB host is a part.',
                           default_value="false"),
            ConfigProperty('tls_ca_file', 'SSL/TLS CA Certificate', ConfigAttributeType.FILE, False, False,
                           description='Specific CA certificate in PEM string format. This is most often the case '
                                       'when using `self-signed` server certificate.',
                           placeholder_value="my_ca_certificate"),
            ConfigProperty('tls_certificate_key_file', 'SSL/TLS Client Certificate', ConfigAttributeType.FILE, False, False,
                           description='Specific client certificate in PEM string format. If the private key for the client '
                                       'certificate is stored in a separate file, it should be concatenated with the certificate file.',
                           placeholder_value="my_client_certificate"),
            ConfigProperty('tls_certificate_key_file_password', 'SSL/TLS Client Key Password', ConfigAttributeType.PASSWORD, False, False,
                           description='If the private key contained in the certificate keyfile is encrypted, users can provide a '
                                       'password or passphrase to decrypt the encrypted private keys.',
                           placeholder_value="my_client_key_password"),
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
                'database': integration['database'],
                'auth_database': integration['auth_database'],
                'source_collection': integration['source_collection'],
                # Optional config keys
                'srv': integration.get('srv', False),
                'port': integration.get('port'),
                'replica_set': integration.get('replica_set'),
                'ssl': integration.get('ssl', False),
                'verify_mode': integration.get('verify_mode', True),
                'direct_connection': integration.get('direct_connection', False),
                'tls_ca_file': integration.get('tls_ca_file'),
                'tls_certificate_key_file': integration.get('tls_certificate_key_file'),
                'tls_certificate_key_file_password': integration.get('tls_certificate_key_file_password'),
            }
        except KeyError as e:
            raise KeyError(f'Integration property `{e}` not found.') from e

    @staticmethod
    def get_client(config: Dict) -> MongoClient:
        connection_string = get_connection_string(config)
        client = MongoClient(connection_string)
        LOGGER.info('Connected to MongoDB host: %s, version: %s',
                    config['host'],
                    client.server_info().get('version', 'unknown'))
        return client


def do_discover(client: MongoClient, config: Dict):
    """
    Executes discovery mode, scanning the MongoDB cluster and converting
    all collections in the specified database into streams. The result is
    output as JSON to stdout.
    Args:
        client (MongoClient): A MongoDB Client instance.
        config (Dict): A dictionary containing database configuration parameters.
    """
    if config['database'] not in get_user_databases(client, config):
        raise NoReadPrivilegeException(config['user'], config['database'])

    database = client[config['database']]
    collection_name = config['source_collection']
    # Check if collection exists
    if collection_name not in database.list_collection_names():
        raise Exception(f'Collection "{collection_name}" not found in the database {config["database"]}.')

    collection = database[collection_name]
    is_view = collection.options().get('viewOn') is not None

    if is_view:
        raise KeyError('The connector does not support views.')

    LOGGER.info("Retrieving collection information for database '%s', collection '%s'", database.name, collection_name)
    streams = [produce_collection_schema(collection)]
    json.dump({'streams': streams}, sys.stdout, indent=2)

    return streams


def clear_state_on_replication_change(stream: Dict, state: Dict, replication_method: str) -> Dict:
    """
    Resets the state for a given stream if the replication method has changed.
    Args:
        stream (Dict): A dictionary representing a stream.
        state (Dict): The current state of the replication process.
        replication_method (str): The desired replication method.

    Returns:
        Dict: The updated state.
    """
    md_map = metadata.to_map(stream['metadata'])
    tap_stream_id = stream['tap_stream_id']

    # Change in replication method detected
    current_replication_method = md_map.get('replication-method', replication_method)
    last_replication_method = singer.get_bookmark(state, tap_stream_id, 'last_replication_method')
    if last_replication_method is not None and (current_replication_method != last_replication_method):
        log_msg = (f"Detected change in replication method for stream {tap_stream_id}. Changing from"
                   f" {last_replication_method} to {current_replication_method}. Re-replicating entire collection.")
        LOGGER.info(log_msg)
        state = singer.reset_stream(state, tap_stream_id)

    state = singer.write_bookmark(state, tap_stream_id, 'last_replication_method', current_replication_method)

    return state


def sync_traditional_stream(client: MongoClient, stream: Dict, state: Dict, replication_method: str):
    """
    Syncs the stream using a traditional replication method i.e. FULL_TABLE.
    Args:
        client (MongoClient): An instance of the MongoClient.
        stream (Dict): A dictionary representing the stream to be synced.
        state (Dict): The current state of the replication process.
        replication_method (str): The desired replication method.

    Raises:
        InvalidReplicationMethodException: If the replication method is not either FULL_TABLE or LOG_BASED.
    """
    tap_stream_id = stream['tap_stream_id']

    common.COUNTS[tap_stream_id] = 0
    common.TIMES[tap_stream_id] = 0
    common.SCHEMA_COUNT[tap_stream_id] = 0
    common.SCHEMA_TIMES[tap_stream_id] = 0

    md_map = metadata.to_map(stream['metadata'])
    replication_method = md_map.get('replication-method', replication_method)

    if replication_method not in {LOG_BASED_METHOD, FULL_TABLE_METHOD}:
        raise InvalidReplicationMethodException(replication_method,
                                                'replication method needs to be either FULL_TABLE'
                                                ' or LOG_BASED')

    database_name = metadata.get(md_map, (), 'database-name')

    # Emit a state message to indicate that we've started this stream
    state = clear_state_on_replication_change(stream, state, replication_method)
    state = singer.set_currently_syncing(state, stream['tap_stream_id'])
    singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

    write_schema_message(stream)
    common.SCHEMA_COUNT[tap_stream_id] += 1

    with metrics.job_timer('sync_table') as timer:
        timer.tags['database'] = database_name
        timer.tags['table'] = stream['table_name']

        collection = client[database_name][stream["table_name"]]
        full_table.sync_database(collection, stream, state)

    state = singer.set_currently_syncing(state, None)

    singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))


def sync_traditional_streams(client: MongoClient, traditional_streams: List[Dict], state: Dict,
                             replication_method: str):
    """
    This function syncs a list of traditional streams that use FULL_TABLE replication method, one stream at a time.
    Args:
        client (MongoClient): A MongoClient instance used to connect to the MongoDB database.
        traditional_streams (List[Dict]): A list of dictionaries, where each dictionary represents a traditional stream to be synced.
        state (Dict): A dictionary representing the current state of the sync.
        replication_method (str): A string representing the replication method to use for syncing the streams.
    """
    for stream in traditional_streams:
        sync_traditional_stream(client, stream, state, replication_method)


def sync_log_based_streams(client: MongoClient,
                           log_based_streams: List[Dict],
                           database_name: str,
                           state: Dict,
                           replication_method: str
                           ):
    """
    Sync log_based streams all at once by listening on the database-level change streams events.
    Args:
        client: MongoDB client instance
        log_based_streams:  list of streams to sync
        database_name: name of the database to sync from
        state: state dictionary
        replication_method: replication method
    """
    if not log_based_streams:
        return

    streams = streams_list_to_dict(log_based_streams)

    for tap_stream_id, stream in streams.items():
        common.COUNTS[tap_stream_id] = 0
        common.TIMES[tap_stream_id] = 0
        common.SCHEMA_COUNT[tap_stream_id] = 0
        common.SCHEMA_TIMES[tap_stream_id] = 0

        state = clear_state_on_replication_change(stream, state, replication_method)
        singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

        write_schema_message(stream)
        common.SCHEMA_COUNT[tap_stream_id] += 1

    with metrics.job_timer('sync_table') as timer:
        timer.tags['database'] = database_name

        log_based.sync_database(client[database_name], streams, state)

    state = singer.set_currently_syncing(state, None)
    singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))


def do_sync(client: MongoClient, catalog: Dict, config: Dict, replication_method: str, state: Dict):
    """
    Syncs all the selected streams in the catalog
    Args:
        client: MongoDb client instance
        catalog: dictionary with all the streams details
        config: config dictionary
        replication_method: replication method
        state: state
    """

    all_streams = catalog['streams']
    streams_to_sync = get_streams_to_sync(all_streams, state)

    log_based_streams, traditional_streams = filter_streams_by_replication_method(streams_to_sync,
                                                                                  replication_method)
    LOGGER.debug('Starting sync of traditional streams ...')
    sync_traditional_streams(client, traditional_streams, state, replication_method)
    LOGGER.debug('Sync of traditional streams done')

    LOGGER.debug('Starting sync of log based streams ...')
    sync_log_based_streams(client,
                           log_based_streams,
                           config['database'],
                           state,
                           replication_method
                           )
    LOGGER.debug('Sync of log based streams done')

    LOGGER.info(common.get_sync_summary(catalog, replication_method))


def main_impl():
    """
    Main function
    """
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)
    config = args.config
    srv = config.get('srv', False)

    if not srv:
        args = utils.parse_args(REQUIRED_CONFIG_KEYS_NON_SRV)
        config = args.config
    try:
        config = create_certficate_files(config)
        connection_string = get_connection_string(config)
        client = MongoClient(connection_string)

        LOGGER.info('Connected to MongoDB host: %s, version: %s',
                    config['host'],
                    client.server_info().get('version', 'unknown'))

        if args.discover:
            do_discover(client, config)
        elif args.catalog:
            state = args.state or {}
            do_sync(client, args.catalog.to_dict(), config, args.config.get('replication_method', FULL_TABLE_METHOD), state)
    except Exception as e:
        delete_certficate_files(config)
        raise e
    delete_certficate_files(config)


def main():
    """
    Main
    """
    try:
        main_impl()
    except Exception as exc:
        LOGGER.exception(exc)
        raise exc
