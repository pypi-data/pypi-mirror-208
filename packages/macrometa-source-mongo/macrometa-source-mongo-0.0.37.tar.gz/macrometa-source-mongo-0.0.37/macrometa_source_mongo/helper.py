#!/usr/bin/env python3
from typing import Dict, Optional, List, Tuple

import singer
from c8connector import SchemaAttributeType
from pymongo.collection import Collection
from singer import get_logger, metadata, SchemaMessage, write_message

from macrometa_source_mongo.sync_strategies.common import calculate_destination_stream_name

logger = get_logger('macrometa_source_mongo')


def get_replication_method_from_stream(stream: Dict, replication_method: str) -> Optional[str]:
    """
    Retrieves the replication method for a given stream.
    Args:
        stream (Dict): A stream dictionary.
        replication_method (str): The replication method.

    Returns:
        Optional[str]: The found replication method for the stream if defined, None otherwise.
    """
    md_map = metadata.to_map(stream['metadata'])
    return md_map.get('replication-method', replication_method)


def is_log_based_stream(stream: Dict, replication_method: str) -> bool:
    """
    Determines if the given stream uses log-based replication method.
    Args:
        stream (Dict): A stream dictionary.
        replication_method (str): The replication method.
    Returns:
        bool: True if the stream uses log-based replication, False otherwise.
    """
    return get_replication_method_from_stream(stream, replication_method) == 'LOG_BASED'


def write_schema_message(stream: Dict):
    """
    Constructs and writes a stream schema message to stdout.
    Args:
        stream (Dict): A stream catalog dictionary.
    """
    write_message(SchemaMessage(
        stream=calculate_destination_stream_name(stream),
        schema=stream['schema'],
        key_properties=['_id']))


def is_stream_selected(stream: Dict) -> bool:
    """
    Determines if the given stream is selected for syncing based on its metadata.
    Args:
        stream (Dict): A stream dictionary.

    Returns:
        bool: True if the stream is selected for syncing, False otherwise.
    """
    mdata = metadata.to_map(stream['metadata'])
    is_selected = metadata.get(mdata, (), 'selected')

    return is_selected is True


def streams_list_to_dict(streams: List[Dict]) -> Dict[str, Dict]:
    """
    Transforms a list of streams into a dictionary, using stream IDs as keys and stream dictionaries as values.

    Args:
        streams (List[Dict]): A list of stream dictionaries.

    Returns:
        Dict[str, Dict]: A dictionary of streams, where the keys are the stream IDs
         and the values are the stream dictionaries.
    """
    return {stream['tap_stream_id']: stream for stream in streams}


def filter_streams_by_replication_method(streams_to_sync: List[Dict], replication_method: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Splits the list of streams into two separate lists based on their replication method: log-based
    or traditional (full table).
    Args:
        streams_to_sync (List[Dict]): A list of streams selected for syncing.
        replication_method (str): The desired replication method ('LOG_BASED' or 'FULL_TABLE').
    Returns:
        Tuple[List[Dict], List[Dict]]: A tuple containing two lists - the first list contains log-based streams,
                                   and the second list contains traditional (full table) streams.
    """
    log_based_streams = []
    non_log_based_streams = []

    for stream in streams_to_sync:
        if replication_method == 'LOG_BASED':
            log_based_streams.append(stream)
            non_log_based_streams.append(stream)
        elif is_log_based_stream(stream, replication_method):
            log_based_streams.append(stream)
        else:
            non_log_based_streams.append(stream)

    return log_based_streams, non_log_based_streams


def get_streams_to_sync(streams: List[Dict], state: Dict) -> List:
    """
    Filters the list of streams to return only those selected for syncing, ordering them based on their state.
    Args:
        streams (List[Dict]): A list of all discovered streams.
        state (Dict): The state dictionary containing bookmarks for each stream.

    Returns:
        List: A list of selected streams, ordered from those without state to those with state.
    """

    selected_streams = [stream for stream in streams if is_stream_selected(stream)]

    # Separate streams with and without state (unprocessed streams to get priority)
    streams_with_state = []
    streams_without_state = []

    for stream in selected_streams:
        if state.get('bookmarks', {}).get(stream['tap_stream_id']):
            streams_with_state.append(stream)
        else:
            streams_without_state.append(stream)

    ordered_streams = streams_without_state + streams_with_state

    if not (currently_syncing := singer.get_currently_syncing(state)):
        return ordered_streams

    currently_syncing_stream = list(filter(
        lambda s: s['tap_stream_id'] == currently_syncing,
        ordered_streams))
    non_currently_syncing_streams = list(filter(lambda s: s['tap_stream_id'] != currently_syncing, ordered_streams))

    return currently_syncing_stream + non_currently_syncing_streams


def produce_collection_schema(collection: Collection) -> Dict:
    """
    Create a schema dictionary for the given collection to be used in discovery mode.

    Args:
        collection (Collection): The MongoDB collection to generate a schema for.
    
    Returns:
        Dict: A dictionary containing the collection schema information, including table_name, 
              stream, metadata, tap_stream_id, and the actual schema.
    """
    collection_name = collection.name
    collection_db_name = collection.database.name

    is_view = collection.options().get('viewOn') is not None

    mdata = {}
    mdata = metadata.write(mdata, (), 'table-key-properties', ['_id'])
    mdata = metadata.write(mdata, (), 'database-name', collection_db_name)
    mdata = metadata.write(mdata, (), 'row-count', collection.estimated_document_count())
    mdata = metadata.write(mdata, (), 'is-view', is_view)

    return {
        'table_name': collection_name,
        'stream': collection_name,
        'metadata': metadata.to_list(mdata),
        'tap_stream_id': f"{collection_db_name}-{collection_name}",
        'schema': {
            'type': 'object',
            'properties': {
                "_id": {
                    "type": ["string", "null"]
                },
                "document": {
                    "type": [
                        "object",
                        "array",
                        "string",
                        "null"
                    ]
                },
                "_sdc_deleted_at": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
            },
        }
    }


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
