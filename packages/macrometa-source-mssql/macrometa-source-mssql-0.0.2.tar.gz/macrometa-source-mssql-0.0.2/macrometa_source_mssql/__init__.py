#!/usr/bin/env python3

import collections
import copy
import itertools

import pkg_resources
import singer
import singer.schema
from c8connector import (
    C8Connector, ConfigProperty, Sample, Schema,
    ConfigAttributeType, SchemaAttributeType, SchemaAttribute)
from singer import metadata, utils
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema as SingerSchema

import macrometa_source_mssql.sync_strategies.common as common
import macrometa_source_mssql.sync_strategies.full_table as full_table
import macrometa_source_mssql.sync_strategies.log_based as log_based
from macrometa_source_mssql.connection import MSSQLConnection, connect_with_backoff
from macrometa_source_mssql.sample_data import modify_reserved_keys, fetch_samples

LOGGER = singer.get_logger('macrometa_source_mssql')

REQUIRED_CONFIG_KEYS = [
    'host',
    'port',
    'user',
    'password',
    'database',
    'filter_dbs',
    'filter_table'
]


class MicrosoftSQLServerConnector(C8Connector):
    """MicrosoftSQLServerConnector's C8Connector impl."""

    def name(self) -> str:
        """Returns the name of the connector."""
        return "Microsoft SQL Server"

    def package_name(self) -> str:
        """Returns the package name of the connector (i.e. PyPi package name)."""
        return "macrometa-source-mssql"

    def version(self) -> str:
        """Returns the version of the connector."""
        return pkg_resources.get_distribution('macrometa_source_mssql').version

    def type(self) -> str:
        """Returns the type of the connector."""
        return "source"

    def description(self) -> str:
        """Returns the description of the connector."""
        return "Source data from a Microsoft SQL Server database table."

    def logo(self) -> str:
        """Returns the logo image for the connector."""
        return ""

    def validate(self, integration: dict) -> None:
        """Validate given configurations against the connector.
        If invalid, throw an exception with the cause.
        """
        try:
            config = self.get_config(integration)
            mssql_conn = MSSQLConnection(config)
            with connect_with_backoff(mssql_conn) as open_conn:
                try:
                    with open_conn.cursor() as cur:
                        cur.execute("""SELECT @@VERSION as version, @@lock_timeout as lock_wait_timeout""")
                        row = cur.fetchone()
                        LOGGER.info(
                            "Server Parameters: " + "version: %s, " + "lock_timeout: %s, ",
                            *row,
                        )
                except Exception as e:
                    raise e
        except Exception as e:
            raise e

    def samples(self, integration: dict) -> list[Sample]:
        """Fetch sample data using the provided configurations."""
        try:
            config = self.get_config(integration)
            mssql_conn = MSSQLConnection(config)
            catalog = do_discover(mssql_conn, config)
            results = []
            for stream in catalog.streams:
                s_attribs = []
                s_schema = stream.schema
                data = fetch_samples(mssql_conn, config, stream)[:10]
                # Appending _ to keys for preserving values of reserved keys in source data
                reserved_keys = ['_key', '_id', '_rev']
                if stream.metadata[0]['metadata'].get('table-key-properties'):
                    key_properties = stream.metadata[0]['metadata'].get('table-key-properties')
                    if key_properties[0] == '_key':
                        reserved_keys.remove('_key')
                s_schema.properties = modify_reserved_keys(s_schema.properties, reserved_keys)

                for k, v in s_schema.properties.items():
                    t = v.type[-1]
                    s_attribs.append(SchemaAttribute(k, self.get_attribute_type(t)))
                schema = Schema(stream.stream, s_attribs)
                results.append(Sample(
                    schema=schema,
                    data=data)
                )
        except Exception as e:
            LOGGER.info("Exception raised: %s", e)
            raise e
        return results

    def schemas(self, integration: dict) -> list[Schema]:
        """Get supported schemas using the given configurations."""
        try:
            config = self.get_config(integration)
            mssql_conn = MSSQLConnection(config)
            catalog = do_discover(mssql_conn, config)
            results = []
            for stream in catalog.streams:
                s_attribs = []
                s_schema = stream.schema

                # Appending _ to keys for preserving values of reserved keys in source data
                reserved_keys = ['_key', '_id', '_rev']
                if stream.metadata[0]['metadata'].get('table-key-properties'):
                    key_properties = stream.metadata[0]['metadata'].get('table-key-properties')
                    if key_properties[0] == '_key':
                        reserved_keys.remove('_key')
                s_schema.properties = modify_reserved_keys(s_schema.properties, reserved_keys)

                for k, v in s_schema.properties.items():
                    t = v.type[-1]
                    s_attribs.append(SchemaAttribute(k, self.get_attribute_type(t)))
                results.append(Schema(stream.stream, s_attribs))
        except Exception as e:
            LOGGER.info("Exception raised: %s", e)
            raise e
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
                           description='Microsoft SQL Server host.', placeholder_value='mssql_host'),
            ConfigProperty('port', 'Port', ConfigAttributeType.INT, True, False,
                           description='Microsoft SQL Server port.', default_value='1433'),
            ConfigProperty('user', 'Username', ConfigAttributeType.STRING, True, False,
                           description='Microsoft SQL Server user.', default_value='admin'),
            ConfigProperty('password', 'Password', ConfigAttributeType.PASSWORD, True, False,
                           description='Microsoft SQL Server password.', placeholder_value='password'),
            ConfigProperty('database', 'Database Name', ConfigAttributeType.STRING, True, True,
                           description='Microsoft SQL Server database name.', default_value='master'),
            ConfigProperty('filter_dbs', 'Source Schema', ConfigAttributeType.STRING, True, True,
                           description='Source Schema to scan.', placeholder_value='my_schema'),
            ConfigProperty('filter_table', 'Source Table', ConfigAttributeType.STRING, True, True,
                           description='Source Table to scan.', placeholder_value='my_table'),
            ConfigProperty('default_replication_method', 'Replication Method', ConfigAttributeType.STRING, True, True,
                           description='Choose from LOG_BASED, FULL_TABLE.', default_value='FULL_TABLE'),
            ConfigProperty('characterset', 'Character Set', ConfigAttributeType.STRING, False, False,
                           description='The characterset of the Microsoft SQL Server database.', default_value='utf8'),
            ConfigProperty('tds_version', 'TDS Version', ConfigAttributeType.STRING, False, False,
                           description='Set the version of TDS to use when communicating with MS SQL Server.',
                           default_value='7.3'),
            ConfigProperty('use_date_datatype', 'Use Date data type', ConfigAttributeType.BOOLEAN, False, False,
                           description='Emit `datetime` type values as a date without a time component or time without '
                                       'an UTC offset.', default_value='false'),
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
                'port': integration['port'],
                'user': integration['user'],
                'password': integration['password'],
                'database': integration['database'],
                'filter_dbs': integration['filter_dbs'],
                'filter_table': integration['filter_table'],

                # Optional config keys
                'characterset': integration.get('characterset', "utf8"),
                'tds_version': integration.get('tds_version', "7.3"),
                'use_date_datatype': integration.get('use_date_datatype', False),
                'default_replication_method': integration.get('default_replication_method', "FULL_TABLE")
            }
        except KeyError as e:
            raise KeyError(f'Integration property `{e}` not found.') from e


Column = collections.namedtuple(
    "Column",
    [
        "table_schema",
        "table_name",
        "column_name",
        "data_type",
        "character_maximum_length",
        "numeric_precision",
        "numeric_scale",
        "is_primary_key",
    ],
)

STRING_TYPES = {"char", "enum", "longtext", "mediumtext", "text", "varchar", "uniqueidentifier", "nvarchar", "nchar"}
BYTES_FOR_INTEGER_TYPE = {
    "tinyint": 1,
    "smallint": 2,
    "mediumint": 3,
    "int": 4,
    "bigint": 8,
}
FLOAT_TYPES = {"float", "double", "real"}
DECIMAL_TYPES = {"decimal", "number", "money", "smallmoney", "numeric"}
DATETIME_TYPES = {"datetime2", "datetime", "timestamp", "smalldatetime"}
DATE_TYPES = {"date"}
TIME_TYPES = {"time"}
VARIANT_TYPES = {"json"}


def default_date_format():
    return False


def schema_for_column(c, config):
    """Returns the Schema object for the given Column."""
    data_type = c.data_type.lower()

    inclusion = "available"

    use_date_data_type_format = config.get("use_date_datatype") or default_date_format()

    if c.is_primary_key == 1:
        inclusion = "automatic"

    result = SingerSchema(inclusion=inclusion)

    if data_type == "bit":
        result.type = ["null", "boolean"]

    elif data_type in BYTES_FOR_INTEGER_TYPE:
        result.type = ["null", "integer"]
        bits = BYTES_FOR_INTEGER_TYPE[data_type] * 8
        result.minimum = 0 - 2 ** (bits - 1)
        result.maximum = 2 ** (bits - 1) - 1

    elif data_type in FLOAT_TYPES:
        result.type = ["null", "number"]
        result.multipleOf = 10 ** (0 - (c.numeric_scale or 17))

    elif data_type in DECIMAL_TYPES:
        result.type = ["null", "number"]
        result.multipleOf = 10 ** (0 - c.numeric_scale)
        return result

    elif data_type in STRING_TYPES:
        result.type = ["null", "string"]
        # When length is -1 it is a long column type
        # https://docs.microsoft.com/en-us/sql/relational-databases/system-information-schema-views/columns-transact-sql?view=sql-server-ver15
        # -1 is not valid JSON schema
        # https://json-schema.org/understanding-json-schema/reference/string.html#length
        if c.character_maximum_length != -1:
            result.maxLength = c.character_maximum_length

    elif data_type in DATETIME_TYPES:
        result.type = ["null", "string"]
        result.format = "date-time"

    elif data_type in DATE_TYPES:
        if use_date_data_type_format:
            result.type = ["null", "string"]
            result.format = "date"
        else:
            result.type = ["null", "string"]
            result.format = "date-time"

    elif data_type in TIME_TYPES:
        if use_date_data_type_format:
            result.type = ["null", "string"]
            result.format = "time"
        else:
            result.type = ["null", "string"]
            result.format = "date-time"

    elif data_type in VARIANT_TYPES:
        result.type = ["null", "object"]

    else:
        result = SingerSchema(
            None,
            inclusion="unsupported",
            description="Unsupported column type",
        )
    return result


def create_column_metadata(cols, config):
    mdata = {}
    mdata = metadata.write(mdata, (), "selected-by-default", False)
    for c in cols:
        schema = schema_for_column(c, config)
        mdata = metadata.write(
            mdata,
            ("properties", c.column_name),
            "selected-by-default",
            schema.inclusion != "unsupported",
        )
        mdata = metadata.write(
            mdata, ("properties", c.column_name), "sql-datatype", c.data_type.lower()
        )

    return metadata.to_list(mdata)


def discover_catalog(mssql_conn, config):
    """Returns a Catalog describing the structure of the database."""
    LOGGER.info("Preparing Catalog")
    mssql_conn = MSSQLConnection(config)
    filter_dbs_config = config.get("filter_dbs")

    if filter_dbs_config:
        filter_dbs_clause = ",".join(["'{}'".format(db) for db in filter_dbs_config.split(",")])

        table_schema_clause = "WHERE c.table_schema IN ({})".format(filter_dbs_clause)
    else:
        table_schema_clause = """
        WHERE c.table_schema NOT IN (
        'information_schema',
        'INFORMATION_SCHEMA',
        'performance_schema',
        'sys'
        )"""

    with connect_with_backoff(mssql_conn) as open_conn:
        cur = open_conn.cursor()
        LOGGER.info("Fetching tables")
        cur.execute(
            """SELECT table_schema,
                table_name,
                table_type
            FROM INFORMATION_SCHEMA.tables c
            {}
        """.format(
                table_schema_clause
            )
        )
        table_info = {}

        for (db, table, table_type) in cur.fetchall():
            if db not in table_info:
                table_info[db] = {}

            table_info[db][table] = {"row_count": None, "is_view": table_type == "VIEW"}
        LOGGER.info("Tables fetched, fetching columns")
        cur.execute(
            """with constraint_columns as (
                select c.table_schema
                , c.table_name
                , c.column_name

                from INFORMATION_SCHEMA.constraint_column_usage c

                join INFORMATION_SCHEMA.table_constraints tc
                        on tc.table_schema = c.table_schema
                        and tc.table_name = c.table_name
                        and tc.constraint_name = c.constraint_name
                        and tc.constraint_type in ('PRIMARY KEY', 'UNIQUE'))
                SELECT c.table_schema,
                    c.table_name,
                    c.column_name,
                    data_type,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    case when cc.column_name is null then 0 else 1 end
                FROM INFORMATION_SCHEMA.columns c

                left join constraint_columns cc
                    on cc.table_name = c.table_name
                    and cc.table_schema = c.table_schema
                    and cc.column_name = c.column_name

                {}
                ORDER BY c.table_schema, c.table_name
        """.format(
                table_schema_clause
            )
        )
        columns = []
        rec = cur.fetchone()
        while rec is not None:
            columns.append(Column(*rec))
            rec = cur.fetchone()
        LOGGER.info("Columns Fetched")
        entries = []
        for (k, cols) in itertools.groupby(columns, lambda c: (c.table_schema, c.table_name)):
            cols = list(cols)
            (table_schema, table_name) = k
            schema = SingerSchema(
                type="object",
                properties={c.column_name: schema_for_column(c, config) for c in cols},
            )
            md = create_column_metadata(cols, config)
            md_map = metadata.to_map(md)

            md_map = metadata.write(md_map, (), "database-name", table_schema)

            is_view = table_info[table_schema][table_name]["is_view"]

            if table_schema in table_info and table_name in table_info[table_schema]:
                row_count = table_info[table_schema][table_name].get("row_count")

                if row_count is not None:
                    md_map = metadata.write(md_map, (), "row-count", row_count)

                md_map = metadata.write(md_map, (), "is-view", is_view)

            key_properties = [c.column_name for c in cols if c.is_primary_key == 1]

            md_map = metadata.write(md_map, (), "table-key-properties", key_properties)

            entry = CatalogEntry(
                table=table_name,
                stream=table_name,
                metadata=metadata.to_list(md_map),
                tap_stream_id=common.generate_tap_stream_id(table_schema, table_name),
                schema=schema,
            )

            entries.append(entry)
    LOGGER.info("Catalog ready")
    return Catalog(entries)


def do_discover(mssql_conn, config):
    catalog = discover_catalog(mssql_conn, config)
    catalog.dump()
    return catalog


def desired_columns(selected, table_schema):
    """Return the set of column names we need to include in the SELECT.

    selected - set of column names marked as selected in the input catalog
    table_schema - the most recently discovered SingerSchema for the table
    """
    all_columns = set()
    available = set()
    automatic = set()
    unsupported = set()

    for column, column_schema in table_schema.properties.items():
        all_columns.add(column)
        inclusion = column_schema.inclusion
        if inclusion == "automatic":
            automatic.add(column)
        elif inclusion == "available":
            available.add(column)
        elif inclusion == "unsupported":
            unsupported.add(column)
        else:
            raise Exception("Unknown inclusion " + inclusion)

    selected_but_unsupported = selected.intersection(unsupported)
    if selected_but_unsupported:
        LOGGER.warning(
            "Columns %s were selected but are not supported. Skipping them.",
            selected_but_unsupported,
        )

    selected_but_nonexistent = selected.difference(all_columns)
    if selected_but_nonexistent:
        LOGGER.warning("Columns %s were selected but do not exist.", selected_but_nonexistent)

    not_selected_but_automatic = automatic.difference(selected)
    if not_selected_but_automatic:
        LOGGER.warning(
            "Columns %s are primary keys but were not selected. Adding them.",
            not_selected_but_automatic,
        )

    return selected.intersection(available).union(automatic)


def is_valid_currently_syncing_stream(selected_stream, state):
    stream_metadata = metadata.to_map(selected_stream.metadata)
    replication_method = stream_metadata.get((), {}).get("replication-method")

    if replication_method != "LOG_BASED":
        return True

    if replication_method == "LOG_BASED" and cdc_stream_requires_historical(selected_stream, state):
        return True

    return False


def cdc_stream_requires_historical(catalog_entry, state):
    current_lsn = singer.get_bookmark(state, catalog_entry.tap_stream_id, "lsn")

    max_lsn_values = singer.get_bookmark(state, catalog_entry.tap_stream_id, "max_lsn_values")

    last_lsn_fetched = singer.get_bookmark(state, catalog_entry.tap_stream_id, "last_lsn_fetched")

    if (current_lsn) and (not max_lsn_values and not last_lsn_fetched):
        return False

    return True


def resolve_catalog(discovered_catalog, streams_to_sync):
    result = Catalog(streams=[])

    # Iterate over the streams in the input catalog and match each one up
    # with the same stream in the discovered catalog.
    for catalog_entry in streams_to_sync:
        catalog_metadata = metadata.to_map(catalog_entry.metadata)
        replication_key = catalog_metadata.get((), {}).get("replication-key")

        discovered_table = discovered_catalog.get_stream(catalog_entry.tap_stream_id)
        database_name = common.get_database_name(catalog_entry)

        if not discovered_table:
            LOGGER.warning(
                "Database %s table %s was selected but does not exist",
                database_name,
                catalog_entry.table,
            )
            continue

        selected = {
            k
            for k, v in discovered_table.schema.properties.items()
            if common.property_is_selected(catalog_entry, k) or k == replication_key
        }

        # These are the columns we need to select
        columns = desired_columns(selected, discovered_table.schema)
        result.streams.append(
            CatalogEntry(
                tap_stream_id=catalog_entry.tap_stream_id,
                metadata=catalog_entry.metadata,
                stream=catalog_entry.tap_stream_id,
                table=catalog_entry.table,
                schema=SingerSchema(
                    type="object",
                    properties={col: discovered_table.schema.properties[col] for col in columns},
                ),
            )
        )

    return result


def get_non_cdc_streams(mssql_conn, catalog, config, state):
    """Method to discover all connections which will not use CDC

    Returns the Catalog of data we're going to sync for all SELECT-based streams
    (i.e. FULL_TABLE, and LOG_BASED that require a historical sync).
    LOG_BASED streams that require a historical sync are inferred from lack
    of any state.

    Using the Catalog provided from the input file, this function will return a
    Catalog representing exactly which tables and columns that will be emitted
    by SELECT-based syncs. This is achieved by comparing the input Catalog to a
    freshly discovered Catalog to determine the resulting Catalog.

    The resulting Catalog will include the following any streams marked as
    "selected" that currently exist in the database. Columns marked as "selected"
    and those labled "automatic" (e.g. primary keys and replication keys) will be
    included. Streams will be prioritized in the following order:
      1. currently_syncing if it is SELECT-based
      2. any streams that do not have state
      3. any streams that do not have a replication method of LOG_BASED
    """
    mssql_conn = MSSQLConnection(config)
    discovered = discover_catalog(mssql_conn, config)

    # Filter catalog to include only selected streams
    selected_streams = list(filter(lambda s: common.stream_is_selected(s), catalog.streams))
    streams_with_state = []
    streams_without_state = []

    for stream in selected_streams:
        stream_metadata = metadata.to_map(stream.metadata)
        # if stream_metadata.table in ["aagaggpercols", "aagaggdef"]:
        for k, v in stream_metadata.get((), {}).items():
            LOGGER.info(f"{k}: {v}")
            # LOGGER.info(stream_metadata.get((), {}).get("table-key-properties"))
        replication_method = stream_metadata.get((), {}).get("replication-method")
        stream_state = state.get("bookmarks", {}).get(stream.tap_stream_id)

        if not stream_state:
            if replication_method == "LOG_BASED":
                LOGGER.info(
                    "LOG_BASED stream %s requires full historical sync", stream.tap_stream_id
                )

            streams_without_state.append(stream)
        elif (
                stream_state
                and replication_method == "LOG_BASED"
                and cdc_stream_requires_historical(stream, state)
        ):
            is_view = common.get_is_view(stream)

            if is_view:
                raise Exception(
                    "Unable to replicate stream({}) with cdc because it is a view.".format(
                        stream.stream
                    )
                )

            LOGGER.info("LOG_BASED stream %s will resume its historical sync", stream.tap_stream_id)

            streams_with_state.append(stream)
        elif stream_state and replication_method != "LOG_BASED":
            streams_with_state.append(stream)

    # If the state says we were in the middle of processing a stream, skip
    # to that stream. Then process streams without prior state and finally
    # move onto streams with state (i.e. have been synced in the past)
    currently_syncing = singer.get_currently_syncing(state)

    # prioritize streams that have not been processed
    ordered_streams = streams_without_state + streams_with_state

    if currently_syncing:
        currently_syncing_stream = list(
            filter(
                lambda s: s.tap_stream_id == currently_syncing
                          and is_valid_currently_syncing_stream(s, state),
                streams_with_state,
            )
        )

        non_currently_syncing_streams = list(
            filter(lambda s: s.tap_stream_id != currently_syncing, ordered_streams)
        )

        streams_to_sync = currently_syncing_stream + non_currently_syncing_streams
    else:
        # prioritize streams that have not been processed
        streams_to_sync = ordered_streams

    return resolve_catalog(discovered, streams_to_sync)


def get_cdc_streams(mssql_conn, catalog, config, state):
    discovered = discover_catalog(mssql_conn, config)

    selected_streams = list(filter(lambda s: common.stream_is_selected(s), catalog.streams))
    cdc_streams = []

    for stream in selected_streams:
        stream_metadata = metadata.to_map(stream.metadata)
        replication_method = stream_metadata.get((), {}).get("replication-method")

        if replication_method == "LOG_BASED" and not cdc_stream_requires_historical(stream, state):
            cdc_streams.append(stream)

    return resolve_catalog(discovered, cdc_streams)


def write_schema_message(catalog_entry, bookmark_properties=[]):
    key_properties = common.get_key_properties(catalog_entry)

    singer.write_message(
        singer.SchemaMessage(
            stream=catalog_entry.stream,
            schema=catalog_entry.schema.to_dict(),
            key_properties=key_properties,
            bookmark_properties=bookmark_properties,
        )
    )


def do_sync_historical_log(mssql_conn, config, catalog_entry, state, columns):
    mssql_conn = MSSQLConnection(config)

    # Add additional keys to the schema
    log_based.add_synthetic_keys_to_schema(catalog_entry)

    write_schema_message(catalog_entry)

    stream_version = common.get_stream_version(catalog_entry.tap_stream_id, state)

    # full_table.sync_table(mssql_conn, config, catalog_entry, state, columns, stream_version)
    log_based.sync_historic_table(mssql_conn, config, catalog_entry, state, columns, stream_version)

    # Prefer initial_full_table_complete going forward
    singer.clear_bookmark(state, catalog_entry.tap_stream_id, "version")

    state = singer.write_bookmark(
        state, catalog_entry.tap_stream_id, "initial_full_table_complete", True
    )

    singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))


def do_sync_full_table(mssql_conn, config, catalog_entry, state, columns):
    mssql_conn = MSSQLConnection(config)

    write_schema_message(catalog_entry)

    stream_version = common.get_stream_version(catalog_entry.tap_stream_id, state)

    full_table.sync_table(mssql_conn, config, catalog_entry, state, columns, stream_version)

    # Prefer initial_full_table_complete going forward
    singer.clear_bookmark(state, catalog_entry.tap_stream_id, "version")

    state = singer.write_bookmark(
        state, catalog_entry.tap_stream_id, "initial_full_table_complete", True
    )

    singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))


def do_sync_log_based(mssql_conn, config, catalog_entry, state, columns):
    mssql_conn = MSSQLConnection(config)
    md_map = metadata.to_map(catalog_entry.metadata)
    stream_version = common.get_stream_version(catalog_entry.tap_stream_id, state)
    replication_key = md_map.get((), {}).get("replication-key")
    # Add additional keys to the schema
    log_based.add_synthetic_keys_to_schema(catalog_entry)

    write_schema_message(catalog_entry=catalog_entry, bookmark_properties=[replication_key])
    LOGGER.info("SingerSchema written")
    stream_version = common.get_stream_version(catalog_entry.tap_stream_id, state)
    log_based.sync_table(mssql_conn, config, catalog_entry, state, columns, stream_version)

    singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))


def sync_non_cdc_streams(mssql_conn, non_cdc_catalog, config, state):
    mssql_conn = MSSQLConnection(config)

    for catalog_entry in non_cdc_catalog.streams:
        columns = list(catalog_entry.schema.properties.keys())

        if not columns:
            LOGGER.warning(
                "There are no columns selected for stream %s, skipping it.", catalog_entry.stream
            )
            continue

        state = singer.set_currently_syncing(state, catalog_entry.tap_stream_id)

        # Emit a state message to indicate that we've started this stream
        singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

        md_map = metadata.to_map(catalog_entry.metadata)
        replication_method = md_map.get((), {}).get("replication-method")
        start_lsn = md_map.get((), {}).get("lsn")
        LOGGER.info(f"Table {catalog_entry.table} proposes {replication_method} sync")
        if not replication_method and config.get("default_replication_method"):
            replication_method = config.get("default_replication_method")
            LOGGER.info(
                f"Table {catalog_entry.table} reverting to DEFAULT {replication_method} sync"
            )

        if replication_method == "LOG_BASED" and not start_lsn:
            LOGGER.info(f"No initial load for {catalog_entry.table}, using full table replication")
        else:
            LOGGER.info(f"Table {catalog_entry.table} will use {replication_method} sync")

        if replication_method == "FULL_TABLE":
            LOGGER.info(f"syncing {catalog_entry.table} full table")
            do_sync_full_table(mssql_conn, config, catalog_entry, state, columns)
        elif replication_method == "LOG_BASED":
            LOGGER.info(f"syncing {catalog_entry.table} cdc tables")
            do_sync_historical_log(mssql_conn, config, catalog_entry, state, columns)
        else:
            raise Exception(
                "only LOG_BASED and FULL TABLE replication methods are supported"
            )

    state = singer.set_currently_syncing(state, None)
    singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))


def sync_cdc_streams(mssql_conn, cdc_catalog, config, state):
    mssql_conn = MSSQLConnection(config)

    if cdc_catalog.streams:
        for catalog_entry in cdc_catalog.streams:
            columns = list(catalog_entry.schema.properties.keys())
            if not columns:
                LOGGER.warning(
                    "There are no columns selected for stream %s, skipping it.",
                    catalog_entry.stream,
                )
                continue

            state = singer.set_currently_syncing(state, catalog_entry.tap_stream_id)

            # Emit a state message to indicate that we've started this stream
            singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

            md_map = metadata.to_map(catalog_entry.metadata)
            replication_method = md_map.get((), {}).get("replication-method")
            LOGGER.info(f"Table {catalog_entry.table} proposes {replication_method} sync")
            LOGGER.info(f"Table {catalog_entry.table} will use {replication_method} sync")

            if replication_method == "LOG_BASED":
                LOGGER.info(f"syncing {catalog_entry.table} cdc tables")
                do_sync_log_based(mssql_conn, config, catalog_entry, state, columns)
            else:
                raise Exception("only LOG_BASED methods are supported for CDC")

        state = singer.set_currently_syncing(state, None)
        singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))


def do_sync(mssql_conn, config, catalog, state):
    LOGGER.info("Beginning sync")
    non_cdc_catalog = get_non_cdc_streams(mssql_conn, catalog, config, state)
    cdc_catalog = get_cdc_streams(mssql_conn, catalog, config, state)

    for entry in non_cdc_catalog.streams:
        LOGGER.info(f"Need to sync {entry.table}")
    sync_non_cdc_streams(mssql_conn, non_cdc_catalog, config, state)
    sync_cdc_streams(mssql_conn, cdc_catalog, config, state)


def log_server_params(mssql_conn):
    with connect_with_backoff(mssql_conn) as open_conn:
        try:
            with open_conn.cursor() as cur:
                cur.execute("""SELECT @@VERSION as version, @@lock_timeout as lock_wait_timeout""")
                row = cur.fetchone()
                LOGGER.info(
                    "Server Parameters: " + "version: %s, " + "lock_timeout: %s, ",
                    *row,
                )
        except:
            LOGGER.warning("Encountered error checking server params.")


def main_impl():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)
    mssql_conn = MSSQLConnection(args.config)
    log_server_params(mssql_conn)

    if args.discover:
        do_discover(mssql_conn, args.config)
    elif args.catalog:
        state = args.state or {}
        do_sync(mssql_conn, args.config, args.catalog, state)
    elif args.properties:
        catalog = Catalog.from_dict(args.properties)
        state = args.state or {}
        do_sync(mssql_conn, args.config, catalog, state)
    else:
        LOGGER.info("No properties were selected")


def main():
    try:
        main_impl()
    except Exception as exc:
        LOGGER.critical(exc)
        raise exc
