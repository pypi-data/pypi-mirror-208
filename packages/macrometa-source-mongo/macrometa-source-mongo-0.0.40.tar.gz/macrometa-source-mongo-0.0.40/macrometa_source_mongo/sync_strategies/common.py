#!/usr/bin/env python3
import base64
import datetime
import time
import uuid
import bson
import singer
import pytz
import tzlocal

from typing import Dict, Any, Optional
from bson import objectid, timestamp, datetime as bson_datetime
from singer import utils, metadata
from terminaltables import AsciiTable

from macrometa_source_mongo.exceptions import InvalidDateTimeException, SyncException, UnsupportedKeyTypeException

SDC_DELETED_AT = "_sdc_deleted_at"
COUNTS = {}
TIMES = {}
SCHEMA_COUNT = {}
SCHEMA_TIMES = {}


def should_sync_column(md_map, field_name):
    field_metadata = md_map.get(('properties', field_name), {})
    return singer.should_sync_field(field_metadata.get('inclusion'),
                                    field_metadata.get('selected'),
                                    True)


def calculate_destination_stream_name(stream: Dict) -> str:
    """
    Constructs the appropriate stream name for use in Singer messages.

    Args:
        stream: A dictionary containing stream information.
    
    Returns:
        A string representing the stream name.
    """
    s_md = metadata.to_map(stream['metadata'])
    return f"{s_md.get((), {}).get('database-name')}-{stream['stream']}"


def get_stream_version(tap_stream_id: str, state: Dict) -> int:
    """
    Retrieves the stream version from the given state dictionary or generates a new one if not present.
    Args:
        tap_stream_id: The stream ID for which the version is needed.
        state: The state dictionary from which to extract the version, if it exists.

    Returns:
       The version as an integer.
    """
    stream_version = singer.get_bookmark(state, tap_stream_id, 'version')

    if stream_version is None:
        stream_version = int(time.time() * 1000)

    return stream_version


def class_to_string(key_value: Any, key_type: str) -> str:
    """
    Transforms various data types into their string representations.
    Supported types include: datetime, bson Timestamp, bytes, int, Int64, float, ObjectId, str, and UUID.
    Args:
        key_value: The value to be converted into a string.
        key_type: The data type of the value.

    Returns:
        The string representation of the given value.

    Raises:
        UnsupportedKeyTypeException: If the specified key_type is not supported.
    """
    if key_type == 'datetime':
        if key_value.tzinfo is None:
            timezone = tzlocal.get_localzone()
            local_datetime = timezone.localize(key_value)
            utc_datetime = local_datetime.astimezone(pytz.UTC)
        else:
            utc_datetime = key_value.astimezone(pytz.UTC)

        return utils.strftime(utc_datetime)

    if key_type == 'Timestamp':
        return f'{key_value.time}.{key_value.inc}'

    if key_type == 'bytes':
        return base64.b64encode(key_value).decode('utf-8')

    if key_type in {'int', 'Int64', 'float', 'ObjectId', 'str', 'UUID'}:
        return str(key_value)

    raise UnsupportedKeyTypeException(f"The key type {key_value} is not supported")


def string_to_class(str_value: str, type_value: str) -> Any:
    """
    Converts the specified string value to the given type, if the type is supported.
    
    Supported types include: UUID, datetime, int, Int64, float, ObjectId, Timestamp, bytes, and str.
    
    Args:
        str_value (str): The string value to convert.
        type_value (str): The type of the value.
        
    Returns:
        Any: The converted string value.
    
    Raises:
        UnsupportedKeyTypeException: If the key is not supported.
    """
    conversion = {
        'UUID': uuid.UUID,
        'datetime': singer.utils.strptime_with_tz,
        'int': int,
        'Int64': bson.int64.Int64,
        'float': str,
        'ObjectId': objectid.ObjectId,
        'Timestamp': lambda val: (lambda split_value=val.split('.'):
                                  bson.timestamp.Timestamp(int(split_value[0]), int(split_value[1])))(),
        'bytes': lambda val: base64.b64decode(val.encode()),
        'str': str,
    }

    if type_value in conversion:
        return conversion[type_value](str_value)

    raise UnsupportedKeyTypeException(f"The key type {type_value} is not supported")


def safe_transform_datetime(value: datetime.datetime, path):
    """
    Transforms a datetime object safely from local time zone to UTC if possible.

    Args:
        value (datetime.datetime): The datetime object to be transformed.
        path (Any): The path to the value.

    Returns:
        str: The UTC datetime as a string.
    """
    timezone = tzlocal.get_localzone()
    try:
        local_datetime = timezone.localize(value)
        utc_datetime = local_datetime.astimezone(pytz.UTC)
    except Exception as ex:
        if str(ex) == "year is out of range" and value.year == 0:
            # formatting it as a string and passing it along
            return f"{value.year:04d}-{value.month:02d}-{value.day:02d}T{value.hour:02d}:{value.minute:02d}:" \
                   f"{value.second:02d}.{value.microsecond:06d}Z"
        raise InvalidDateTimeException(f"Datetime Invalid at [{'.'.join(map(str, path))}]: {value}") from ex
    return utils.strftime(utc_datetime)


def transform_value(value: Any, path) -> Any:
    """
    Transforms a value to a format suitable for JSON.

    Args:
        value (Any): The value to be transformed.
        path (Any): The path to the value.

    Returns:
        Any: The transformed value.
    """
    conversion = {
        list: lambda val, pat: list(map(lambda v: transform_value(v[1], pat + [v[0]]), enumerate(val))),
        dict: lambda val, pat: {k: transform_value(v, pat + [k]) for k, v in val.items()},
        uuid.UUID: lambda val, _: class_to_string(val, 'UUID'),
        objectid.ObjectId: lambda val, _: class_to_string(val, 'ObjectId'),
        bson_datetime.datetime: safe_transform_datetime,
        timestamp.Timestamp: lambda val, _: utils.strftime(val.as_datetime()),
        bson.int64.Int64: lambda val, _: class_to_string(val, 'Int64'),
        bytes: lambda val, _: class_to_string(val, 'bytes'),
        datetime.datetime: lambda val, _: class_to_string(val, 'datetime'),
        bson.decimal128.Decimal128: lambda val, _: val.to_decimal(),
        bson.regex.Regex: lambda val, _: dict(pattern=val.pattern, flags=val.flags),
        bson.code.Code: lambda val, _: dict(value=str(val), scope=str(val.scope)) if val.scope else str(val),
        bson.dbref.DBRef: lambda val, _: dict(id=str(val.id), collection=val.collection, database=val.database),
    }

    if isinstance(value, tuple(conversion.keys())):
        return conversion[type(value)](value, path)

    return value


def row_to_singer_record(stream: Dict,
                         row: Dict,
                         time_extracted: datetime.datetime,
                         time_deleted: Optional[datetime.datetime],
                         version: Optional[int] = None,
                         ) -> singer.RecordMessage:
    """
    Converts a row to a Singer RecordMessage instance.

    Args:
        stream (Dict): A dictionary containing details for the stream.
        row (Dict): A dictionary containing the row to be converted.
        time_extracted (datetime.datetime): The time when the row was extracted.
        time_deleted (Optional[datetime.datetime]): The time when the row was deleted, if applicable.
        version (Optional[int]): The version of the stream.
        
    Returns:
        singer.RecordMessage: A Singer RecordMessage instance.
    """

    if version is None:
        version = int(time.time() * 1000)

    try:
        row_to_persist = {k: transform_value(v, [k]) for k, v in row.items()
                          if not isinstance(v, (bson.min_key.MinKey, bson.max_key.MaxKey))}
    except InvalidDateTimeException as ex:
        raise SyncException(
            f"Encountered an error while syncing collection: {stream['tap_stream_id']},"
            " record ID: {row['_id']} - {ex}") from ex

    row_to_persist = {
        '_id': str(row_to_persist['_id']),
        'document': row_to_persist,
        SDC_DELETED_AT: utils.strftime(time_deleted) if time_deleted else None
    }

    return singer.RecordMessage(
        stream=calculate_destination_stream_name(stream),
        record=row_to_persist,
        version=version,
        time_extracted=time_extracted)


def get_sync_summary(catalog, replication_method: str)->str:
    """
    Constructs a summary of the synchronization for all streams.
    Args:
    catalog (dict): A dictionary containing details for all the streams.
    replication_method (str): The replication method being used.

    Returns: 
        str: A string representation of the summary table.
    """
    headers = [['database',
                'collection',
                'replication method',
                'total records',
                'write speed',
                'total time',
                'schemas written',
                'schema build duration',
                'percent building schemas']]

    rows = []
    for stream_id, stream_count in COUNTS.items():
        stream = [x for x in catalog['streams'] if x['tap_stream_id'] == stream_id][0]
        collection_name = stream.get("table_name")
        md_map = metadata.to_map(stream['metadata'])
        db_name = metadata.get(md_map, (), 'database-name')
        replication_method = md_map.get('replication-method', replication_method)

        stream_time = TIMES[stream_id]
        schemas_written = SCHEMA_COUNT[stream_id]
        schema_duration = SCHEMA_TIMES[stream_id]

        if stream_time == 0:
            stream_time = 0.000001

        rows.append(
            [
                db_name,
                collection_name,
                replication_method,
                f'{stream_count} records',
                f'{stream_count / float(stream_time):.1f} records/second',
                f'{stream_time:.5f} seconds',
                f'{schemas_written} schemas',
                f'{schema_duration:.5f} seconds',
                f'{100 * schema_duration / float(stream_time):.2f}%'
            ]
        )

    data = headers + rows
    table = AsciiTable(data, title='Sync Summary')

    return '\n\n' + table.table
