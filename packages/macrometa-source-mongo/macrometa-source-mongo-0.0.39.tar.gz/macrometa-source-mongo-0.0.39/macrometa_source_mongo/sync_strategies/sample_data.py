import bson
import pymongo

from singer import metadata
from macrometa_source_mongo.sync_strategies import common

from macrometa_source_mongo.exceptions import InvalidDateTimeException, SyncException

def fetch_table(client, conn_info, stream):
    """
    Fetches data from a MongoDB collection for a specified stream.

    Args:
        client (pymongo.MongoClient): A MongoClient instance connected to the MongoDB server.
        conn_info (dict): A dictionary containing connection information, such as host, port, and database name.
        stream (dict): A dictionary containing information about the stream, such as table name and stream ID.

    Returns:
        Tuple containing the schema for the stream and data fetched from the MongoDB collection.
    """
    database = client[conn_info['dbname']]
    collection = database[stream["table_name"]]
    data = []
    rec = {}
    cursor = collection.find({}, sort=[("_id", pymongo.ASCENDING)]).limit(10)

    for row in cursor:
        try:
            rec = {k: common.transform_value(v, [k]) for k, v in row.items()
                              if not isinstance(v, (bson.min_key.MinKey, bson.max_key.MaxKey))}
        except InvalidDateTimeException as ex:
            raise SyncException(
                f"Error syncing collection {stream['tap_stream_id']}, object ID {row['_id']} - {ex}") from ex

        rec = {
            '_id': str(rec['_id']),
            'document': rec
        }
        data.append(rec)

    schema = {"_id": "string", "document": "object"}
    return schema, data


def fetch_samples(client, conn_config, stream):
    """
    Fetches samples of data from a MongoDB collection for a specified stream.

    Args:
        client (pymongo.MongoClient): A MongoClient instance connected to the MongoDB server.
        conn_config (dict): A dictionary containing connection configuration information.
        stream (dict): A dictionary containing information about the stream, such as table name and stream ID.

    Returns:
        Tuple containing the schema for the stream and sample data fetched from the MongoDB collection.
    """
    md_map = metadata.to_map(stream['metadata'])
    conn_config['dbname'] = md_map.get(()).get('database-name')
    return fetch_table(client, conn_config, stream)
