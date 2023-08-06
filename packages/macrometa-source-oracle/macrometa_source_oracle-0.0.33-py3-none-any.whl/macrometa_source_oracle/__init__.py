#!/usr/bin/env python3
# pylint: disable=missing-docstring,not-an-iterable,too-many-locals,too-many-arguments,invalid-name

import collections
import copy
import itertools

import pkg_resources
import singer
import singer.schema
from c8connector import C8Connector, ConfigProperty, Sample, SchemaAttribute, SchemaAttributeType, ConfigAttributeType
from c8connector import Schema as C8Schema
from singer import utils, metadata, get_bookmark
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema

import macrometa_source_oracle.connection as orc_db
import macrometa_source_oracle.sync_strategies.common as common
import macrometa_source_oracle.sync_strategies.full_table as full_table
import macrometa_source_oracle.sync_strategies.log_based as log_based

LOGGER = singer.get_logger()

# LogMiner do not support LONG, LONG RAW, CLOB, BLOB, NCLOB, ADT, or COLLECTION datatypes.
Column = collections.namedtuple('Column', [
    "table_schema",
    "table_name",
    "column_name",
    "data_type",
    "data_length",
    "char_length",
    "character_used",
    "numeric_precision",
    "numeric_scale"
])

STRING_TYPES = {'char', 'nchar', 'varchar', 'varchar2', 'nvarchar2'}

FLOAT_TYPES = {'binary_float', 'binary_double'}

REQUIRED_CONFIG_KEYS = [
    'host',
    'port',
    'user',
    'password',
    'service_name'
]


class OracleSourceConnector(C8Connector):
    """OracleSourceConnector's C8Connector impl."""

    def name(self) -> str:
        """Returns the name of the connector."""
        return "OracleDB"

    def package_name(self) -> str:
        """Returns the package name of the connector (i.e. PyPi package name)."""
        return "macrometa-source-oracle"

    def version(self) -> str:
        """Returns the version of the connector."""
        return pkg_resources.get_distribution('macrometa_source_oracle').version

    def type(self) -> str:
        """Returns the type of the connector."""
        return "source"

    def description(self) -> str:
        """Returns the description of the connector."""
        return "Source data from an OracleDB table."

    def logo(self) -> str:
        """Returns the logo image for the connector."""
        return ""

    def validate(self, integration: dict) -> None:
        """Validate given configurations against the connector.
        If invalid, throw an exception with the cause.
        """
        config, filter_schema = self.get_config(integration)
        try:
            config = orc_db.create_wallet_file(config)
            do_discovery(config, [filter_schema], config['filter_table'])
        except Exception as e:
            LOGGER.info('Exception raised: %s', e)
            orc_db.delete_wallet_file(config)
            raise e
        orc_db.delete_wallet_file(config)

    def schemas(self, integration: dict) -> list[C8Schema]:
        """Get supported schemas using the given configurations."""
        config, filter_schema = self.get_config(integration)
        try:
            config = orc_db.create_wallet_file(config)
            catalog = do_discovery(config, [filter_schema], config['filter_table'])
            results = []
            for stream in catalog.streams:
                s_attribs = []
                s_schema = stream.schema

                # Appending _ to keys for preserving values of reserved keys in source data
                reserved_keys = ['_key', '_id', '_rev']
                metadata_obj = stream.metadata[0]
                if metadata_obj['metadata'].get('table-key-properties'):
                    key_properties = metadata_obj['metadata'].get(
                        'table-key-properties')
                    if key_properties[0] == '_key':
                        reserved_keys.remove('_key')
                properties = s_schema.properties
                modified_properties = orc_db.modify_reserved_keys(
                    properties, reserved_keys)
                s_schema.properties = modified_properties

                for k, v in s_schema.properties.items():
                    t = v.type[-1]
                    s_attribs.append(SchemaAttribute(
                        k, self.get_attribute_type(t)))
                results.append(C8Schema(stream.stream, s_attribs))
        except Exception as e:
            LOGGER.info('Exception raised: %s', e)
            orc_db.delete_wallet_file(config)
            raise e
        orc_db.delete_wallet_file(config)
        return results

    def samples(self, integration: dict) -> list[Sample]:
        """Fetch sample data using the given configurations."""
        config, filter_schema = self.get_config(integration)
        try:
            config = orc_db.create_wallet_file(config)
            catalog = do_discovery(config, [filter_schema], config['filter_table'])
            results = []
            for stream in catalog.streams:
                s_attribs = []
                s_schema = stream.schema

                data = orc_db.fetch_samples(config, stream)
                # Appending _ to keys for preserving values of reserved keys in source data
                reserved_keys = ['_key', '_id', '_rev']
                metadata_obj = stream.metadata[0]
                if metadata_obj['metadata'].get('table-key-properties'):
                    key_properties = metadata_obj['metadata'].get(
                        'table-key-properties')
                    if key_properties[0] == '_key':
                        reserved_keys.remove('_key')
                properties = s_schema.properties
                modified_properties = orc_db.modify_reserved_keys(
                    properties, reserved_keys)
                s_schema.properties = modified_properties

                for k, v in s_schema.properties.items():
                    t = v.type[-1]
                    s_attribs.append(SchemaAttribute(
                        k, self.get_attribute_type(t)))
                schema = C8Schema(stream.stream, s_attribs)
                results.append(Sample(
                    schema=schema,
                    data=data)
                )
        except Exception as e:
            LOGGER.info('Exception raised: %s', e)
            orc_db.delete_wallet_file(config)
            raise e
        orc_db.delete_wallet_file(config)
        return results

    def reserved_keys(self) -> list[str]:
        """List of reserved keys for the connector."""
        return []

    def config(self) -> list[ConfigProperty]:
        """Get configuration parameters for the connector."""
        return [
            ConfigProperty('host', 'Host', ConfigAttributeType.STRING, True, False,
                           description='Oracle DB host.',
                           placeholder_value='oracle_host'),
            ConfigProperty('port', 'Port', ConfigAttributeType.INT, True, False,
                           description='Oracle DB port.',
                           placeholder_value='1521'),
            ConfigProperty('user', 'Username', ConfigAttributeType.STRING, True, False,
                           description='Oracle DB username.',
                           placeholder_value='system'),
            ConfigProperty('password', 'Password', ConfigAttributeType.STRING, True, False,
                           description='Oracle DB user password.',
                           placeholder_value='password'),
            ConfigProperty('default_replication_method', 'Default Replication Method',
                           ConfigAttributeType.STRING, True, False,
                           description='Choose from LOG_BASED, FULL_TABLE.',
                           default_value='FULL_TABLE'),
            ConfigProperty('filter_schema', 'Source Schema', ConfigAttributeType.STRING, True, False,
                           description='Source Schema to scan.',
                           placeholder_value='C##CUSTOMERS'),
            ConfigProperty('filter_table', 'Source Table', ConfigAttributeType.STRING, True, False,
                           description='Source Table to scan.',
                           placeholder_value='my_table'),
            ConfigProperty('service_name', 'Service Name', ConfigAttributeType.STRING, True, False,
                           description='Oracle DB service name.',
                           placeholder_value='ORCLCDB'),
            ConfigProperty('multitenant', 'Multi-Tenant', ConfigAttributeType.BOOLEAN, False, False,
                           description='Is Oracle DB is multi tenant or not.',
                           default_value='false'),
            ConfigProperty('pdb_name', 'Pluggable Database Name', ConfigAttributeType.STRING, False, False,
                           description='Oracle portable db name.',
                           placeholder_value='ORCLPDB1'),
            ConfigProperty('scn_window_size', 'SCN Window Size', ConfigAttributeType.INT, False, False,
                           description='Oracle SCN window size to mine in a single iteration for logminer replication (LOG_BASED).',
                           default_value='100'),
            ConfigProperty('polling_interval', 'Polling Interval', ConfigAttributeType.INT, False, False,
                           description='The number of seconds the connector should wait after a fetch data attempt returned empty results. This is only applicable for LOG_BASED replication method.',
                           default_value='60'),
            ConfigProperty('ewallet_pem', 'Client ewallet.pem file (Enables SSL/TLS connection)', ConfigAttributeType.STRING, False, False,
                           description='Specify the content of ewallet.pem file here. This enables SSL/TLS connection using the oracle wallet of the client. If ewallet.pem file is not present then'
                                       ' convert ewallet.p12 to ewallet.pem using any third party tool or from the script mentioned here'
                                       '(https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html#creating-a-pem-file-for-python-oracledb-thin-mode)',
                           placeholder_value='my_ewallet_pem'),
            ConfigProperty('wallet_password', 'Wallet Password', ConfigAttributeType.STRING, False, False,
                           description='Specifies the password for the PEM file (ewallet.pem). If Oracle Cloud was used to download the wallet, then the parameter should be set to the password created in the cloud console when downloading the wallet.',
                           placeholder_value='my_wallet_password'),
        ]

    def capabilities(self) -> list[str]:
        """Return the capabilities[1] of the connector.
        [1] https://docs.meltano.com/contribute/plugins#how-to-test-a-tap
        """
        return ['catalog', 'discover', 'state']

    @staticmethod
    def get_attribute_type(source_type: str) -> SchemaAttributeType:
        if source_type == 'string':
            return SchemaAttributeType.STRING
        elif source_type == 'integer':
            return SchemaAttributeType.INT
        elif source_type == 'boolean':
            return SchemaAttributeType.BOOLEAN
        elif source_type == 'number':
            return SchemaAttributeType.DOUBLE
        else:
            return SchemaAttributeType.OBJECT

    @staticmethod
    def get_config(integration: dict):
        try:
            config = {
                'host': integration['host'],
                'user': integration['user'],
                'password': integration['password'],
                'port': integration['port'],
                'service_name': integration['service_name'],
                'multitenant': integration.get('multitenant', False),
                'filter_table': integration['filter_table'],
                # Optional
                'pdb_name': integration.get('pdb_name', 'CDB$ROOT'),
                'scn_window_size': integration.get('scn_window_size', log_based.SCN_WINDOW_SIZE),
                'polling_interval': integration.get('polling_interval', log_based.POLLING_INTERVAL),
                'ewallet_pem': integration.get('ewallet_pem'),
                'wallet_password': integration.get('wallet_password'),
            }

            filter_schema = integration['filter_schema']
            return config, filter_schema
        except KeyError as e:
            raise KeyError(f'Integration property `{e}` not found.') from e


def nullable_column(col_name, col_type, pks_for_table):
    """
    Check if a column should be nullable.

    :param col_name: Name of the column.
    :type col_name: str
    :param col_type: Type of the column.
    :type col_type: str
    :param pks_for_table: List of primary key column names for the table.
    :type pks_for_table: list
    :return: List containing the column type if the column is a primary key, or ['null', col_type] otherwise.
    :rtype: list
    """
    return [col_type] if col_name in pks_for_table else ['null', col_type]


def schema_for_column(c, pks_for_table):
    """
    Generate a Schema object for the given column and primary keys.

    :param c: Column object.
    :type c: Column
    :param pks_for_table: List of primary key column names for the table.
    :type pks_for_table: list
    :return: Schema object for the column.
    :rtype: Schema
    """
    # To prevent calling lower() on a column with no datatype.
    if c.data_type is None:
        LOGGER.info('Skipping column %s since it had no datatype', c.column_name)
        return Schema(None)

    data_type = c.data_type.lower()
    result = Schema()

    # If the scale is None, it means that the default value is 6 digits.
    numeric_scale = c.numeric_scale

    if data_type == 'number' and numeric_scale is not None and numeric_scale <= 0:
        return get_schema(c, pks_for_table, result, 'integer')

    elif data_type == 'number':
        # We are utilizing a custom singer.decimal string formatter, which does not consider scale/precision,
        # due to the discrepancies in scale and precision among numeric types and Oracle versions.
        return get_schema(c, pks_for_table, result, 'string', 'singer.decimal')

    elif data_type == 'date' or data_type.startswith("timestamp"):
        return get_schema(c, pks_for_table, result, 'string', 'date-time')

    elif data_type in FLOAT_TYPES:
        return get_schema(c, pks_for_table, result, 'number')

    elif data_type in STRING_TYPES:
        return get_schema(c, pks_for_table, result, 'string', schema_character='C')

    # The column types "float", "double_precision", and "real" are perplexing.
    # They are not actually IEEE754 floats; instead, they are depicted as decimals.
    # Nonetheless, it seems that we cannot determine their maximum or minimum values.
    elif data_type in ['float', 'double_precision']:
        return get_schema(c, pks_for_table, result, 'string', 'singer.decimal')

    return Schema(None)


def get_schema(c, pks_for_table, result, schema_type, schema_format=None, schema_character=None):
    """
    Update and return the Schema object for the given column and primary keys.

    :param c: Column object.
    :type c: Column
    :param pks_for_table: List of primary key column names for the table.
    :type pks_for_table: list
    :param result: Schema object to update.
    :type result: Schema
    :param schema_type: Type of the schema.
    :type schema_type: str
    :param schema_format: Format of the schema (optional).
    :type schema_format: str, optional
    :param schema_character: Character used for the schema (optional).
    :type schema_character: str, optional
    :return: Updated Schema object.
    :rtype: Schema
    """
    result.type = nullable_column(c.column_name, schema_type, pks_for_table)
    if schema_format:
        result.format = schema_format
    if schema_character:
        character_used = c.character_used
        if character_used == schema_character:
            result.maxLength = c.char_length

    return result


def filter_schemas_sql_clause(sql, binds_sql, filter_table, owner_schema=None):
    """
    Generate an SQL query with filter schemas and table clause.

    :param sql: SQL query string.
    :type sql: str
    :param binds_sql: List of binds for the SQL query.
    :type binds_sql: list
    :param filter_table: Name of the table to filter by.
    :type filter_table: str
    :param owner_schema: Owner schema name (optional).
    :type owner_schema: str, optional
    :return: SQL query string with filter schemas and table clause.
    :rtype: str
    """
    if binds_sql:
        if owner_schema:
            return f"""{sql} '{filter_table}' AND {owner_schema}.owner IN ({",".join(binds_sql)})"""
        else:
            return f"""{sql} '{filter_table}' AND owner IN ({",".join(binds_sql)})"""

    else:
        return sql


def produce_row_counts(cur, filter_schemas, filter_table):
    """
    Produce a dictionary of row counts for the filtered schemas and table.

    :param cur: Database cursor object.
    :type cur: Cursor
    :param filter_schemas: List of schemas to filter by.
    :type filter_schemas: list
    :param filter_table: Name of the table to filter by.
    :type filter_table: str
    :return: Dictionary containing row counts for the filtered schemas and table.
    :rtype: dict
    """
    LOGGER.info("Retrieving row count")
    binds_sql = [f":{b}" for b in range(len(filter_schemas))]
    sql = filter_schemas_sql_clause("""
   SELECT table_name, num_rows
   FROM all_tables
   WHERE owner != 'SYS' AND table_name =""", binds_sql, filter_table)

    return {row[0]: row[1] or 0 for row in cur.execute(sql, filter_schemas)}


def produce_pk_constraints(cur, filter_schemas, filter_table):
    """
    Produce a dictionary of primary key constraints for the filtered schemas and table.

    :param cur: Database cursor object.
    :type cur: Cursor
    :param filter_schemas: List of schemas to filter by.
    :type filter_schemas: list
    :param filter_table: Name of the table to filter by.
    :type filter_table: str
    :return: Dictionary containing primary key constraints for the filtered schemas and table.
    :rtype: dict
    """
    LOGGER.info("Retrieveing Primary Key constraints")
    pk_constraints = {}

    binds_sql = [f":{b}" for b in range(len(filter_schemas))]
    sql = filter_schemas_sql_clause("""
   SELECT cols.owner, cols.table_name, cols.column_name
   FROM all_constraints cons, all_cons_columns cols
   WHERE cons.constraint_type = 'P'
   AND cons.constraint_name = cols.constraint_name
   AND cons.owner = cols.owner
   AND cols.owner != 'SYS'
   AND cols.table_name =""", binds_sql, filter_table, "cols")

    for schema, table_name, column_name in cur.execute(sql, filter_schemas):
        if pk_constraints.get(schema) is None:
            pk_constraints[schema] = {}

        if pk_constraints[schema].get(table_name) is None:
            pk_constraints[schema][table_name] = [column_name]
        else:
            pk_constraints[schema][table_name].append(column_name)

    return pk_constraints


def get_database_name(cur):
    """
    Get the name of the database.
    :param cur: Database cursor object.
    :type cur: Cursor
    :return: Name of the database.
    :rtype: str
    """
    rows = cur.execute("SELECT name FROM v$database").fetchall()
    return rows[0][0]


def produce_column_metadata(cur, table_info, table_schema, table_name, pk_constraints, column_schemas, cols):
    """
    Produce metadata for the columns of a given table.
    :param cur: Database cursor object.
    :type cur: Cursor
    :param table_info: Dictionary containing table information.
    :type table_info: dict
    :param table_schema: Name of the table schema.
    :type table_schema: str
    :param table_name: Name of the table.
    :type table_name: str
    :param pk_constraints: Dictionary containing primary key constraints.
    :type pk_constraints: dict
    :param column_schemas: Dictionary containing column schemas.
    :type column_schemas: dict
    :param cols: List of Column objects.
    :type cols: list
    :return: Dictionary containing column metadata.
    :rtype: dict
    """
    mdata = {}

    table_pks = pk_constraints.get(table_schema, {}).get(table_name, [])

    # Unfortunately, certain system tables such as XDB$STATS have primary constraints on columns that do not exist.
    # Therefore, we need to take measures to guard against this.
    table_pks = list(filter(lambda pk: column_schemas.get(pk, Schema(None)).type is not None, table_pks))

    database_name = get_database_name(cur)

    metadata.write(mdata, (), 'table-key-properties', table_pks)
    metadata.write(mdata, (), 'schema-name', table_schema)
    metadata.write(mdata, (), 'database-name', database_name)

    if table_schema in table_info and table_name in table_info[table_schema]:
        metadata.write(mdata, (), 'is-view', table_info[table_schema][table_name]['is_view'])

        row_count = table_info[table_schema][table_name].get('row_count')

        if row_count is not None:
            metadata.write(mdata, (), 'row-count', row_count)

    for c in cols:
        c_name = c.column_name
        # Record the column's data type as its SQL datatype, or "None" if it does not have a datatype
        metadata.write(mdata, ('properties', c_name), 'sql-datatype', (c.data_type or "None"))
        if column_schemas[c_name].type is None:
            mdata = metadata.write(mdata, ('properties', c_name), 'inclusion', 'unsupported')
            mdata = metadata.write(mdata, ('properties', c_name), 'selected-by-default', False)
        elif c_name in pk_constraints.get(table_schema, {}).get(table_name, []):
            mdata = metadata.write(mdata, ('properties', c_name), 'inclusion', 'automatic')
            mdata = metadata.write(mdata, ('properties', c_name), 'selected-by-default', True)
        else:
            mdata = metadata.write(mdata, ('properties', c_name), 'inclusion', 'available')
            mdata = metadata.write(mdata, ('properties', c_name), 'selected-by-default', True)

    return mdata


def discover_columns(cur, table_info, filter_schemas, filter_table):
    """
    Discover columns for the given table and filter schemas, returning a Catalog of entries.

    :param cur: Database cursor object.
    :type cur: Cursor
    :param table_info: Dictionary containing information about tables and views.
    :type table_info: dict
    :param filter_schemas: List of schemas to filter by.
    :type filter_schemas: list
    :param filter_table: Name of the table to filter by.
    :type filter_table: str
    :return: Catalog containing discovered columns for the given filter criteria.
    :rtype: Catalog
    """
    if binds_sql := [f":{b}" for b in range(len(filter_schemas))]:
        sql = """
      SELECT OWNER,
             TABLE_NAME, COLUMN_NAME,
             DATA_TYPE, DATA_LENGTH,
             CHAR_LENGTH, CHAR_USED,
             DATA_PRECISION, DATA_SCALE
        FROM all_tab_columns
       WHERE OWNER != 'SYS' AND owner IN ({}) AND table_name = '{}'
      """.format(",".join(binds_sql), filter_table)
    else:
        sql = """
      SELECT OWNER,
             TABLE_NAME, COLUMN_NAME,
             DATA_TYPE, DATA_LENGTH,
             CHAR_LENGTH, CHAR_USED,
             DATA_PRECISION, DATA_SCALE
        FROM all_tab_columns
       WHERE OWNER != 'SYS' AND table_name = '{}'
      """.format(filter_table)

    LOGGER.info("Retrieving column information")
    cur.execute(sql, filter_schemas)

    columns = []
    counter = 0
    rec = cur.fetchone()
    while rec is not None:
        columns.append(Column(*rec))

        rec = cur.fetchone()

    pk_constraints = produce_pk_constraints(cur, filter_schemas, filter_table)
    entries = []
    for k, cols in itertools.groupby(columns, lambda c: (c.table_schema, c.table_name)):
        cols = list(cols)
        (table_schema, table_name) = k
        pks_for_table = pk_constraints.get(table_schema, {}).get(table_name, [])

        column_schemas = {c.column_name: schema_for_column(c, pks_for_table) for c in cols}
        schema = Schema(type='object', properties=column_schemas)

        md = produce_column_metadata(cur,
                                     table_info,
                                     table_schema,
                                     table_name,
                                     pk_constraints,
                                     column_schemas,
                                     cols)

        entry = CatalogEntry(
            table=table_name,
            stream=table_name,
            metadata=metadata.to_list(md),
            tap_stream_id=f'{table_schema}-{table_name}',
            schema=schema,
        )

        entries.append(entry)

    return Catalog(entries)


def dump_catalog(catalog):
    """
    Dump the contents of the provided catalog object.

    :param catalog: Catalog object containing information about the discovered columns.
    :type catalog: Catalog
    """
    catalog.dump()


def do_discovery(conn_config, filter_schemas, filter_table):
    """
    Perform discovery on the database with the given connection configuration, filter schemas, and filter table.

    :param conn_config: Connection configuration for the database.
    :type conn_config: dict
    :param filter_schemas: List of schemas to filter by.
    :type filter_schemas: list
    :param filter_table: Name of the table to filter by.
    :type filter_table: str
    :return: Catalog containing discovered columns for the given filter criteria.
    :rtype: Catalog
    """
    LOGGER.info("Begin discovering..")
    connection = orc_db.open_connection(conn_config)
    cur = connection.cursor()

    if conn_config['multitenant']:
        LOGGER.info("The database is a multitenant system.")
        # Change session to the anticipated pluggable database (PDB).
        cur.execute(f"ALTER SESSION SET CONTAINER = {conn_config['pdb_name']}")

    row_counts = produce_row_counts(cur, filter_schemas, filter_table)
    table_info = {}

    binds_sql = [f":{b}" for b in range(len(filter_schemas))]

    sql = filter_schemas_sql_clause("""
   SELECT owner, table_name
   FROM all_tables
   WHERE owner != 'SYS' AND table_name =""", binds_sql, filter_table)

    LOGGER.info("Retrieving tables: %s %s", sql, filter_schemas)
    is_view = False
    for row in cur.execute(sql, filter_schemas):
        schema = row[0]
        table = row[1]

        if schema not in table_info:
            table_info[schema] = {}

        table_info[schema][table] = {
            'row_count': row_counts[table],
            'is_view': is_view
        }

    sql = filter_schemas_sql_clause("""
   SELECT owner, view_name
   FROM sys.all_views
   WHERE owner != 'SYS' AND view_name =""", binds_sql, filter_table)

    LOGGER.info("Retrieving views")
    for row in cur.execute(sql, filter_schemas):
        view_name = row[1]
        schema = row[0]

        if schema not in table_info:
            table_info[schema] = {}

        table_info[schema][view_name] = {
            'is_view': True
        }

    if not table_info:
        raise Exception(f'Table/view "{filter_table}" not found in the specified schema {filter_schemas[0]}.')

    for scheme in table_info:
        LOGGER.info(f"Schema {scheme} contains {len(table_info[scheme])} tables/views.")

    catalog = discover_columns(cur, table_info, filter_schemas, filter_table)

    dump_catalog(catalog)
    cur.close()
    connection.close()
    return catalog


def is_selected_via_metadata(stream):
    """
    Check if a stream is selected via its metadata.

    :param stream: Stream object to check.
    :type stream: Stream
    :return: True if the stream is selected, False otherwise.
    :rtype: bool
    """
    table_md = metadata.to_map(stream.metadata).get((), {})
    return table_md.get('selected')


def clear_state_on_replication_change(state, tap_stream_id, replication_method):
    """
    Clear the stream state if the replication method has changed.

    :param state: Current state of the sync process.
    :type state: dict
    :param tap_stream_id: Tap stream ID for the stream.
    :type tap_stream_id: str
    :param replication_method: Replication method for the stream.
    :type replication_method: str
    :return: Updated state after clearing or resetting the stream state.
    :rtype: dict
    """
    # If replication state is changed we reset the state
    last_replication_method = singer.get_bookmark(state, tap_stream_id, 'last_replication_method')
    if last_replication_method is not None and (replication_method != last_replication_method):
        state = singer.reset_stream(state, tap_stream_id)

    state = singer.write_bookmark(state, tap_stream_id, 'last_replication_method', replication_method)
    return state


def classify_streams(streams, state, default_replication_method):
    """
    Classifies streams into traditional and logical streams based on their replication method.

    :param streams: List of streams
    :param state: State object
    :param default_replication_method: Default replication method for streams
    :return: Tuple of a dictionary containing the lookup of stream replication method,
             a list of traditional_streams, and a list of logical_streams
    """
    lookup, traditional_streams, logical_streams = {}, [], []

    for stream in streams:
        stream_metadata = metadata.to_map(stream.metadata)
        replication_method = stream_metadata.get((), {}).get('replication-method', default_replication_method)

        state = clear_state_on_replication_change(state, stream.tap_stream_id, replication_method)
        md_map, desired_columns = get_metadata_and_desired_columns(stream)

        if not is_valid_replication_method(replication_method) or not desired_columns:
            continue

        classify_stream_by_replication_method(stream, state, replication_method, md_map, desired_columns,
                                              lookup, traditional_streams, logical_streams)

    return lookup, traditional_streams, logical_streams


def get_metadata_and_desired_columns(stream):
    """
    Retrieves metadata and desired columns for a given stream.

    :param stream: Stream object
    :return: Tuple containing metadata map and a list of desired columns
    """
    md_map = metadata.to_map(stream.metadata)
    desired_columns = [c for c in stream.schema.properties.keys() if common.should_sync_column(md_map, c)]
    desired_columns.sort()
    return md_map, desired_columns


def is_valid_replication_method(replication_method):
    """
    Checks if the provided replication method is valid.

    :param replication_method: Replication method to check
    :return: True if the replication method is valid, otherwise raises an Exception
    """
    valid_replication_methods = {'LOG_BASED', 'FULL_TABLE'}

    if replication_method not in valid_replication_methods:
        raise Exception(f"Invalid replication method {replication_method}")

    return True


def classify_stream_by_replication_method(stream, state, replication_method, md_map, desired_columns,
                                          lookup, traditional_streams, logical_streams):
    """
    Classifies a stream based on its replication method and updates the stream lists accordingly.

    :param stream: Stream object
    :param state: State object
    :param replication_method: Replication method of the stream
    :param md_map: Metadata map for the stream
    :param desired_columns: List of desired columns for the stream
    :param lookup: Dictionary containing the lookup of stream replication methods
    :param traditional_streams: List of traditional_streams
    :param logical_streams: List of logical_streams
    """
    is_view = md_map.get((), {}).get('is-view')
    if replication_method == 'LOG_BASED' and is_view:
        raise Exception(
            f'LogBased replication is NOT supported for views. Please change the replication method for {stream.tap_stream_id}'
        )

    if replication_method == 'FULL_TABLE':
        classify_full_table_stream(stream, lookup, traditional_streams)
    else:  # LOG_BASED
        classify_log_based_stream(stream, state, lookup, traditional_streams, logical_streams)


def classify_full_table_stream(stream, lookup, traditional_streams):
    """
    Classifies a stream as a full table stream and updates the lookup and traditional_streams list.

    :param stream: Stream object
    :param lookup: Dictionary containing the lookup of stream replication methods
    :param traditional_streams: List of traditional_streams
    """
    lookup[stream.tap_stream_id] = 'full'
    traditional_streams.append(stream)


def classify_log_based_stream(stream, state, lookup, traditional_streams, logical_streams):
    """
    Classifies a stream as a log-based stream and updates the lookup, traditional_streams,
    and logical_streams lists.

    :param stream: Stream object
    :param state: State object
    :param lookup: Dictionary containing the lookup of stream replication methods
    :param traditional_streams: List of traditional_streams
    :param logical_streams: List of logical_streams
    """
    scn_bookmark = get_bookmark(state, stream.tap_stream_id, 'scn')
    ora_rowscn_bookmark = get_bookmark(state, stream.tap_stream_id, 'ORA_ROWSCN')

    if not scn_bookmark:
        lookup[stream.tap_stream_id] = 'log_initial'
        traditional_streams.append(stream)
    elif ora_rowscn_bookmark:
        lookup[stream.tap_stream_id] = 'log_initial_interrupted'
        traditional_streams.append(stream)
    else:
        lookup[stream.tap_stream_id] = 'pure_log'
        logical_streams.append(stream)


def sync_traditional_stream(conn_config, stream, state, sync_method, end_scn):
    LOGGER.info("Commencing synchronization of stream (%s) using sync method (%s).", stream.tap_stream_id, sync_method)
    md_map = metadata.to_map(stream.metadata)
    desired_columns = [c for c in stream.schema.properties.keys() if common.should_sync_column(md_map, c)]
    desired_columns.sort()
    if not desired_columns:
        LOGGER.warning('No columns have been selected for stream %s, so it will be skipped.', stream.tap_stream_id)
        return state

    if sync_method == 'full':
        LOGGER.info("Full_table replication is being used for stream %s.", stream.tap_stream_id)
        state = singer.set_currently_syncing(state, stream.tap_stream_id)
        common.send_schema_message(stream, [])
        if md_map.get((), {}).get('is-view'):
            state = full_table.sync_view(conn_config, stream, state, desired_columns)
        else:
            state = full_table.sync_table(conn_config, stream, state, desired_columns)
    elif sync_method == 'log_initial':
        state = singer.set_currently_syncing(state, stream.tap_stream_id)
        LOGGER.info("LogBased replication(Log_miner) is being used for stream %s."
                    " A complete table will be used for the first run.", stream.tap_stream_id)

        state = singer.write_bookmark(state, stream.tap_stream_id, 'scn', end_scn)

        common.send_schema_message(stream, [])
        state = full_table.sync_table(conn_config, stream, state, desired_columns)
    elif sync_method == 'log_initial_interrupted':
        LOGGER.info("First stage of LogBased sync (full table) was interrupted. Resuming it...")
        state = singer.set_currently_syncing(state, stream.tap_stream_id)
        common.send_schema_message(stream, [])
        state = full_table.sync_table(conn_config, stream, state, desired_columns)

    else:
        raise Exception("Invalid sync method {} for stream {}".format(sync_method, stream.tap_stream_id))

    state = singer.set_currently_syncing(state, None)
    singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))
    return state


def sync_traditional_streams(conn_config, traditional_streams, state, sync_method_lookup, end_scn):
    """
    Synchronizes the traditional streams.

    :param conn_config: Connection configuration
    :param traditional_streams: List of traditional_streams
    :param state: State object
    :param sync_method_lookup: Dictionary containing the lookup of stream replication methods
    :param end_scn: End SCN value
    :return: Updated state
    """
    for stream in traditional_streams:
        sync_method = sync_method_lookup[stream.tap_stream_id]
        state = sync_traditional_stream(conn_config, stream, state, sync_method, end_scn)

    return state


def do_sync(conn_config, catalog, default_replication_method, state):
    """
    Main synchronization function.

    :param conn_config: Connection configuration
    :param catalog: Catalog object
    :param default_replication_method: Default replication method for streams
    :param state: State object
    :return: Updated state
    """
    currently_syncing = singer.get_currently_syncing(state)
    streams = sorted(filter(is_selected_via_metadata, catalog.streams), key=lambda s: s.tap_stream_id)
    LOGGER.info("Streams which were sleected: %s ", [s.tap_stream_id for s in streams])

    end_scn = log_based.get_current_scn(conn_config) if any_logical_streams(streams, default_replication_method) else None
    LOGGER.info("End SCN: %s ", end_scn)

    sync_method_lookup, traditional_streams, logical_streams = classify_streams(streams, state, default_replication_method)

    if currently_syncing:
        LOGGER.info("Stream found to be currently syncing: %s", currently_syncing)
        traditional_streams = reorder_traditional_streams(traditional_streams, currently_syncing)
    else:
        LOGGER.info("No stream found to be currently syncing")

    state = sync_traditional_streams(conn_config, traditional_streams, state, sync_method_lookup, end_scn)

    _, _, logical_streams = classify_streams(streams, state, default_replication_method)
    LOGGER.info(f"Logical (LogBased) streams after: {logical_streams}")

    state = sync_log_based_streams(conn_config, list(logical_streams), state, end_scn)
    return state


def reorder_traditional_streams(traditional_streams, currently_syncing):
    """
    Reorder the traditional_streams list, placing the currently syncing stream at the beginning of the list.

    :param traditional_streams: List of traditional streams.
    :type traditional_streams: list
    :param currently_syncing: The stream ID of the currently syncing stream.
    :type currently_syncing: str
    :return: Reordered list of traditional_streams with the currently syncing stream at the beginning.
    :rtype: list
    """
    if currently_syncing_stream := [
        s for s in traditional_streams if s.tap_stream_id == currently_syncing
    ]:
        other_streams = [s for s in traditional_streams if s.tap_stream_id != currently_syncing]
        traditional_streams = currently_syncing_stream + other_streams

    else:
        LOGGER.warning("No stream found currently in syncing state (%s) amongst the raditional streams selected (%s). Ingnoring..",
                       currently_syncing, [s.tap_stream_id for s in traditional_streams])
    return traditional_streams


def sync_log_based_streams(conn_config, log_based_streams, state, end_scn):
    """
    Sync the log-based streams by adding schema properties and updating the state.

    :param conn_config: Connection configuration for the database.
    :type conn_config: dict
    :param log_based_streams: List of log-based streams.
    :type log_based_streams: list
    :param state: Current state of the sync process.
    :type state: dict
    :param end_scn: End System Change Number (SCN) for the sync process.
    :type end_scn: int
    :return: Updated state after syncing log-based streams.
    :rtype: dict
    """
    if log_based_streams:
        log_based_streams = list(map(log_based.add_schema_properties, log_based_streams))
        state = log_based.sync_tables(conn_config, log_based_streams, state, end_scn)

    return state


def any_logical_streams(streams, default_replication_method):
    """
    Determine if there are any logical streams in the provided list of streams.

    :param streams: List of streams to check for logical streams.
    :type streams: list
    :param default_replication_method: The default replication method to use when stream metadata does not specify one.
    :type default_replication_method: str
    :return: True if any logical streams are found, False otherwise.
    :rtype: bool
    """
    for stream in streams:
        stream_metadata = metadata.to_map(stream.metadata)
        replication_method = stream_metadata.get((), {}).get('replication-method', default_replication_method)
        if replication_method == 'LOG_BASED':
            return True

    return False


def main_impl():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)
    conn_config = {'user': args.config['user'],
                   'password': args.config['password'],
                   'host': args.config['host'],
                   'port': args.config['port'],
                   'service_name': args.config['service_name'],
                   'multitenant': args.config.get('multitenant', False),
                   # If PDB name is not specified then we will use CDB$ROOT as the default container 
                   'pdb_name': args.config.get('pdb_name', 'CDB$ROOT'), 
                   'ewallet_pem': args.config.get('ewallet_pem'),
                   'wallet_password': args.config.get('wallet_password'), }

    log_based.SCN_WINDOW_SIZE = int(args.config.get('scn_window_size', log_based.SCN_WINDOW_SIZE))
    log_based.POLLING_INTERVAL = int(args.config.get('polling_interval', log_based.POLLING_INTERVAL))
    try:
        conn_config = orc_db.create_wallet_file(conn_config)
        if args.discover:
            filter_schemas = [args.config.get('filter_schema')]
            filter_table = args.config.get('filter_table')
            do_discovery(conn_config, filter_schemas, filter_table)

        elif args.catalog:
            state = args.state
            do_sync(conn_config, args.catalog, args.config.get('default_replication_method'), state)
        else:
            LOGGER.info("No properties were selected")
    except Exception as e:
        LOGGER.info('Exception raised: %s', e)
        orc_db.delete_wallet_file(conn_config)
        raise e
    orc_db.delete_wallet_file(conn_config)


def main():
    try:
        main_impl()
    except Exception as exc:
        LOGGER.critical(exc)
        raise exc
