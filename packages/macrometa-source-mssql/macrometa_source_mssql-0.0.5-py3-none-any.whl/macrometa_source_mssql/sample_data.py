from singer import metadata, utils

from macrometa_source_mssql import connect_with_backoff
from macrometa_source_mssql.sync_strategies import common
from macrometa_source_mssql.sync_strategies.common import should_sync_column, row_to_singer_record


def fetch_table(mssql_conn, config, stream, desired_columns, limit=10):
    samples = []
    with connect_with_backoff(mssql_conn) as open_conn:
        with open_conn.cursor() as cur:
            select_sql = common.generate_select_sql(stream, desired_columns, limit=limit)
            params = {}
            cur.execute(select_sql, params)
            row = cur.fetchone()
            while row:
                rec_msg = row_to_singer_record(
                    stream, 1, row, desired_columns, utils.now(), config
                )
                samples.append(rec_msg.record)
                row = cur.fetchone()
    return samples


def fetch_samples(mssql_conn, config, stream):
    """
    Fetch samples for the stream.
    """
    md_map = metadata.to_map(stream.metadata)
    desired_columns = [c for c in stream.schema.properties.keys() if should_sync_column(md_map, c)]
    desired_columns.sort()
    if not desired_columns:
        # There are no columns selected for stream. So, skipping it.
        return []
    state = fetch_table(mssql_conn, config, stream, desired_columns, limit=10)

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
