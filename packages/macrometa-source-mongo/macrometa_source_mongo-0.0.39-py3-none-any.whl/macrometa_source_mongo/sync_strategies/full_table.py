#!/usr/bin/env python3
import copy
import time
import pymongo
import singer

from typing import Dict
from pymongo.collection import Collection
from singer import utils

from macrometa_source_mongo.sync_strategies import common

LOGGER = singer.get_logger('macrometa_source_mongo')


def sync_database(collection: Collection, stream: Dict, state: Dict) -> None:
    """
    Sync collection records for FULL_TABLE replication method.
    Args:
        collection: MongoDB collection instance
        stream: dictionary of all stream details
        state: the state
    """
    LOGGER.info('Initiating a full table synchronization for %s.', stream['tap_stream_id'])

    # Check if a table version was previously present before writing it to the state
    first_run = singer.get_bookmark(state, stream['tap_stream_id'], 'version') is None

    # If a bookmark for last_row_count exists, then the previous run was interrupted.
    # Otherwise, choose a new table version.
    last_row_count = singer.get_bookmark(state,
                                          stream['tap_stream_id'],
                                          'last_row_count')
    if last_row_count is not None:
        stream_version = singer.get_bookmark(state, stream['tap_stream_id'], 'version')
    else:
        stream_version = int(time.time() * 1000)
        last_row_count = 0

    state = singer.write_bookmark(state,
                                  stream['tap_stream_id'],
                                  'version',
                                  stream_version)
    singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

    activate_version_message = singer.ActivateVersionMessage(
        stream=common.calculate_destination_stream_name(stream),
        version=stream_version
    )

    # For the first run, send an ACTIVATE_VERSION message
    if first_run:
        singer.write_message(activate_version_message)

    LOGGER.info('Retrieving data from %s with last number of rows counted as: %d', stream['tap_stream_id'], last_row_count)

    with collection.find({},
                         sort=[("_id", pymongo.ASCENDING)]).skip(last_row_count) as cursor:
        rows_saved = last_row_count
        start_time = time.time()

        for row in cursor:
            rows_saved += 1

            singer.write_message(common.row_to_singer_record(stream=stream,
                                                             row=row,
                                                             time_extracted=utils.now(),
                                                             time_deleted=None,
                                                             version=stream_version))

            state = singer.write_bookmark(state,
                                          stream['tap_stream_id'],
                                          'last_row_count',
                                          rows_saved)

            # Write state after every 1000 records
            if rows_saved % 1000 == 0:
                singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

        common.COUNTS[stream['tap_stream_id']] += rows_saved
        common.TIMES[stream['tap_stream_id']] += time.time() - start_time

    singer.clear_bookmark(state, stream['tap_stream_id'], 'last_row_count')

    singer.write_bookmark(state,
                          stream['tap_stream_id'],
                          'initial_full_table_complete',
                          True)

    singer.write_message(activate_version_message)

    LOGGER.info('The number of records synchronized for %s is %s.', stream['tap_stream_id'], rows_saved)
