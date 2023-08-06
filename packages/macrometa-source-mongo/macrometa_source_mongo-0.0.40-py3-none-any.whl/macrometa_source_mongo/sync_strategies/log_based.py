import copy
import time
import singer

from typing import Set, Dict, Optional
from pymongo.database import Database
from pymongo.errors import CursorNotFound
from singer import utils

from macrometa_source_mongo.sync_strategies import common

LOGGER = singer.get_logger('macrometa_source_mongo')

BOOKMARK_KEY = 'token' # bookmark key for logbased replication
DEFAULT_AWAIT_TIME_MS = 600000 # default max await time for database watcher in milliseconds


def update_bookmarks(state: Dict, tap_stream_ids: Set[str], token: Dict) -> Dict:
    """
    Updates the stream state by re-setting the change stream token
    Args:
        state: State dictionary
        tap_stream_ids: set of streams' ID
        token: resume token for LOG_BASED to store as Bookmark

    Returns:
        state: updated state
    """
    for stream in tap_stream_ids:
        state = singer.write_bookmark(state, stream, BOOKMARK_KEY, token)

    return state


def get_bookmark_key_from_state(streams_to_sync: Set[str], state: Dict) -> Optional[Dict]:
    """
    Extract the smallest non null resume token from bookmark key
    Args:
        streams_to_sync: set of log based streams
        state: state dictionary

    Returns: Bookmark key if found, None otherwise

    """
    token_sorted = sorted([stream_state[BOOKMARK_KEY]
                           for stream_name, stream_state in state.get('bookmarks', {}).items()
                           if stream_name in streams_to_sync and stream_state.get(BOOKMARK_KEY) is not None],
                          key=lambda key: key['_data'])

    return token_sorted[0] if token_sorted else None


def sync_database(database: Database,
                  streams_to_sync: Dict[str, Dict],
                  state: Dict,
                  ) -> None:
    """
    Syncs the records from the given collection using Change Stream
    Args:
        database: MongoDB Database instance to sync
        streams_to_sync: Dict of stream dictionary with all the stream details
        state: state dictionary
    """
    LOGGER.info('LogBased sync started for stream "%s" in database "%s"', list(streams_to_sync.keys())[0], database.name)

    rows_saved = {stream_id: 0 for stream_id in streams_to_sync}
    stream_ids = set(streams_to_sync.keys())

    while True:
        start_time = time.time()
        rows_saved_iter_start = rows_saved.copy()
        try:
            # Init a cursor to listen for changes from the last saved resume token
            # if there are no changes after MAX_AWAIT_TIME_MS, the cursor returns an empty batch.
            with database.watch(
                            [{'$match': {
                                '$or': [
                                    {'operationType': 'insert'}, {'operationType': 'update'}, {'operationType': 'delete'}
                                ],
                                '$and': [
                                    # watch collections of selected streams
                                    {'ns.coll': {'$in': [val['table_name'] for val in streams_to_sync.values()]}}
                                ]
                            }}],
                            max_await_time_ms=DEFAULT_AWAIT_TIME_MS,
                            start_after=get_bookmark_key_from_state(stream_ids, state)
                    ) as cursor:
                while cursor.alive:
                
                    change = cursor.try_next()
                    # Get resume token from '_data' to resume LOG_BASED
                    resume_token = {
                        '_data': cursor.resume_token['_data']
                    }
        
                    # After MAX_AWAIT_TIME_MS has elapsed, the cursor will return None.
                    if change is None:
                        continue
                    
                    tap_stream_id = f'{change["ns"]["db"]}-{change["ns"]["coll"]}'
        
                    operation = change['operationType']
        
                    if operation == 'delete':
                        # Delete ops only contain the _id of the row deleted
                        singer.write_message(common.row_to_singer_record(
                            stream=streams_to_sync[tap_stream_id],
                            row={'_id': change['documentKey']['_id']},
                            time_extracted=utils.now(),
                            time_deleted=change[
                                'clusterTime'].as_datetime()))  # returns python's datetime.datetime instance in UTC
        
                        rows_saved[tap_stream_id] += 1
        
                    elif operation == 'insert':
                        singer.write_message(common.row_to_singer_record(stream=streams_to_sync[tap_stream_id],
                                                                         row=change['fullDocument'],
                                                                         time_extracted=utils.now(),
                                                                         time_deleted=None))
        
                        rows_saved[tap_stream_id] += 1
        
                    elif operation == 'update':
                        # update operation only return _id and updated fields in the row,
                        query = {'_id': change['documentKey']['_id']}
                        row = database[streams_to_sync[tap_stream_id]['table_name']].find_one(query)
                        singer.write_message(common.row_to_singer_record(stream=streams_to_sync[tap_stream_id],
                                                                         row=row,
                                                                         time_extracted=utils.now(),
                                                                         time_deleted=None))
        
                        rows_saved[tap_stream_id] += 1
        
                    # update the states of all streams
                    state = update_bookmarks(state, stream_ids, resume_token)
        
                    # Write state after every 1000 records
                    if sum(rows_saved.values()) % 1000 == 0:
                        # write state
                        singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))
        except Exception as e:
            # Log the error
            LOGGER.error('Error received while syncing database: %s', str(e))
            # Retry or exit based on the type of error
            if isinstance(e, CursorNotFound):
                # If the cursor is not found, retry
                LOGGER.info('Cursor not found, retrying...')
                continue
            else:
                # For other types of errors, we may want to exit the program
                LOGGER.error('Unhandled error type, exiting...')
                raise e
        for stream_id in stream_ids:
            common.TIMES[stream_id] += time.time() - start_time
            if rows_saved[stream_id] - rows_saved_iter_start[stream_id] > 0:
                common.COUNTS[stream_id] += (rows_saved[stream_id] - rows_saved_iter_start[stream_id])
                LOGGER.info('The number of records synchronized till now for %s is %s.', stream_id, rows_saved[stream_id])
        time.sleep(10)
