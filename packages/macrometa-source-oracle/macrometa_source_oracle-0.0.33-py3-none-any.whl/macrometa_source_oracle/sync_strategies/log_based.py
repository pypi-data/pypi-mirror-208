#!/usr/bin/env python3
import singer
import decimal
import time
import datetime
from singer import utils, get_bookmark
import singer.metadata as metadata
import singer.metrics as metrics
from singer.schema import Schema
import macrometa_source_oracle.connection as orc_db
import copy
import pytz
import macrometa_source_oracle.sync_strategies.common as common

LOGGER = singer.get_logger()

UPDATE_BOOKMARK_PERIOD = 1000

SCN_WINDOW_SIZE = 100
POLLING_INTERVAL = 60


def get_current_scn(conn_config):
    """
    Get the current SCN from the Oracle instance.
 
    Args:
        conn_config (dict): Connection configuration for the Oracle instance.
 
    Returns:
        int: The current SCN.
    """
    connection = orc_db.open_connection(conn_config)
    cur = connection.cursor()
    current_scn = cur.execute("SELECT current_scn FROM V$DATABASE").fetchall()[0][0]
    cur.close()
    connection.close()
    return current_scn


def add_schema_properties(stream):
    """
    Add 'scn' and '_sdc_deleted_at' properties to the stream schema.
 
    Args:
        stream (Stream): A Stream object.
 
    Returns:
        Stream: The Stream object with updated schema properties.
    """
    stream.schema.properties['scn'] = Schema(type=['integer'])
    stream.schema.properties['_sdc_deleted_at'] = Schema(
        type=['null', 'string'], format='date-time'
    )
    return stream


def  get_stream_version(tap_stream_id, state):
    """
    Get the stream version from the state object based on the tap_stream_id.
 
    Args:
        tap_stream_id (str): The tap stream ID.
        state (dict): The state object.
 
    Returns:
        int: The stream version.
    """
    stream_version = singer.get_bookmark(state, tap_stream_id, 'version')
 
    if stream_version is None:
        raise Exception(f"version not found for log miner {tap_stream_id}")
 
    return stream_version


def row_to_singer_message(stream, row, version, columns, time_extracted):
    """
    Converts a row from the database to a Singer RecordMessage.
 
    Args:
        stream (Stream): The Stream object.
        row (tuple): The row from the database.
        version (int): The stream version.
        columns (list): A list of column names.
        time_extracted (datetime): The extraction time.
 
    Returns:
        singer.RecordMessage: The converted Singer RecordMessage.
    """
    row_to_persist = []
    for idx, elem in enumerate(row):
        column_properties = stream.schema.properties[columns[idx]]
        property_type = column_properties.type
        multiple_of = column_properties.multipleOf
        column_format = column_properties.format
 
        if elem is None:
            row_to_persist.append(elem)
        elif 'integer' in property_type or property_type == 'integer':
            row_to_persist.append(int(elem))
        elif ('number' in property_type or property_type == 'number') and multiple_of:
            row_to_persist.append(decimal.Decimal(elem))
        elif ('number' in property_type or property_type == 'number'):
            row_to_persist.append(float(elem))
        elif column_format == 'date-time':
            row_to_persist.append(elem)
        else:
            row_to_persist.append(elem)
 
    rec = dict(zip(columns, row_to_persist))
    return singer.RecordMessage(
        stream=stream.stream,
        record=rec,
        version=version,
        time_extracted=time_extracted)


def check_db_supplemental_log_level(connection):
    """
    Check if the supplemental log level is set to 'ALL' for the database.
 
    Args:
        connection (Connection): A database connection.
 
    Returns:
        bool: True if the supplemental log level is set to 'ALL', False otherwise.
    """
    cur = connection.cursor()
    cur.execute("SELECT SUPPLEMENTAL_LOG_DATA_ALL FROM V$DATABASE")
    result = cur.fetchone()[0]
    LOGGER.info("Supplemental log data (all) is set to: %s", result)
    cur.close()
    return result == 'YES'


def check_table_supplemental_log_level(stream, connection):
    """
    Check if the supplemental log level is set to 'ALL' for the table.
 
    Args:
        stream (Stream): A Stream object.
        connection (Connection): A database connection.
 
    Returns:
        bool: True if the supplemental log level is set to 'ALL', False otherwise.
    """
    cur = connection.cursor()
    cur.execute(
        """SELECT * FROM ALL_LOG_GROUPS WHERE table_name = :table_name AND LOG_GROUP_TYPE = 'ALL COLUMN LOGGING'""",
        table_name=stream.table
    )
    result = cur.fetchone()
    LOGGER.info("supplemental log level for table(%s): %s", stream.table, result)
    cur.close()
    return result is not None


def setup_session(cur):
    """
    Set up the session with appropriate settings.
 
    Args:
        cur (Cursor): A database cursor.
    """
    cur.execute("ALTER SESSION SET TIME_ZONE = '00:00'")
    cur.execute("""ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD"T"HH24:MI:SS."00+00:00"'""")
    cur.execute("""ALTER SESSION SET NLS_TIMESTAMP_FORMAT='YYYY-MM-DD"T"HH24:MI:SSXFF"+00:00"'""")
    cur.execute("""ALTER SESSION SET NLS_TIMESTAMP_TZ_FORMAT  = 'YYYY-MM-DD"T"HH24:MI:SS.FFTZH:TZM'""")


def sync_tables(conn_config, streams, state, end_scn):
    """
    Sync tables using LogMiner(LOG_BASED) and update state.
 
    Args:
        conn_config (dict): Connection configuration for the Oracle instance.
        streams (list): List of Stream objects.
        state (State): The state of the streams.
        end_scn (int): The ending SCN for LogMiner.
 
    Raises:
        Exception: If supplemental log data is not set to 'ALL' for either the table or the database.
    """
    connection = orc_db.open_connection(conn_config)
    if not check_db_supplemental_log_level(connection):
        for stream in streams:
            if not check_table_supplemental_log_level(stream, connection):
                raise Exception("""
LogBased (logminer) replication failed for stream({}) because supplemental log data is not set to 'ALL' for either the table or the database.
Please run: ALTER DATABASE ADD SUPPLEMENTAL LOG DATA (ALL) COLUMNS;
                """.format(stream.tap_stream_id))
 
    cur = connection.cursor()
    setup_session(cur)
 
    scn_window_size = SCN_WINDOW_SIZE
    start_scn = min([get_bookmark(state, s.tap_stream_id, 'scn') for s in streams])
    end_scn = start_scn + scn_window_size
    scn_received_timestamp = datetime.datetime.utcnow()
    polling_interval = POLLING_INTERVAL
 
    while True:
        state, found = sync_tables_logbased(conn_config, cur, streams, state, start_scn, end_scn)
 
        if found:
            scn_received_timestamp = datetime.datetime.utcnow()
            start_scn = max([get_bookmark(state, s.tap_stream_id, 'scn') for s in streams])
            end_scn = start_scn + scn_window_size
        else:
            time.sleep(polling_interval)
            current_scn = get_current_scn(conn_config)
            end_scn = current_scn + scn_window_size if current_scn >= end_scn else end_scn
 
    cur.close()
    connection.close()

def generate_logmnr_sqls(start_scn, end_scn):
    """
    Generate the SQL statements for LogMiner-related operations.
    
    Args:
        start_scn (int): Starting SCN for LogMiner
        end_scn (int): Ending SCN for LogMiner
    
    Returns:
        tuple: A tuple containing SQL statements for logs_list, add_logmnr, and start_logmnr
    """
    logs_list_sql = f"""
        SELECT ROWNUM, logfilename
        FROM (
            SELECT MEMBER AS logfilename, FIRST_CHANGE#, NEXT_CHANGE#
            FROM gv$log
            INNER JOIN gv$logfile USING (INST_ID, GROUP#)
            WHERE ARCHIVED = 'NO'
            UNION ALL
            SELECT NAME, FIRST_CHANGE#, NEXT_CHANGE#
            FROM gv$archived_log
            WHERE NEXT_CHANGE# BETWEEN {start_scn} AND {end_scn}
            ORDER BY FIRST_CHANGE#
        )"""
 
    add_logmnr_sql = """
        BEGIN
        DBMS_LOGMNR.ADD_LOGFILE(options => DBMS_LOGMNR.{},
                                logfilename => :logfile);
        END;
    """
 
    start_logmnr_sql = f"""
        BEGIN
        DBMS_LOGMNR.START_LOGMNR(
            startScn => {start_scn},
            endScn => {end_scn},
            OPTIONS => DBMS_LOGMNR.DICT_FROM_ONLINE_CATALOG + DBMS_LOGMNR.COMMITTED_DATA_ONLY
        );
        END;
    """
 
    return logs_list_sql, add_logmnr_sql, start_logmnr_sql

def generate_mine_sql(multitenant, pdb_name, redo_value_sql_clause, undo_value_sql_clause):
    """
    Generate the SQL statement for mining operations.
    
    Args:
        multitenant (bool): Whether the Oracle instance is a multitenant or not
        pdb_name (str): The name of the Pluggable Database (PDB) if multitenant is True
        redo_value_sql_clause (str): SQL clause for extracting redo values
        undo_value_sql_clause (str): SQL clause for extracting undo values
    
    Returns:
        str: SQL statement for mining operations
    """
    return (
        f"""
            SELECT OPERATION, SQL_REDO, SCN, CSCN, COMMIT_TIMESTAMP, {redo_value_sql_clause}, {undo_value_sql_clause}
            FROM v$logmnr_contents
            WHERE table_name = :table_name AND seg_owner = :seg_owner
            AND operation IN ('INSERT', 'UPDATE', 'DELETE')
            AND SRC_CON_UID = (SELECT CON_UID FROM v$pdbs WHERE upper(name) = upper('{pdb_name}'))
        """
        if multitenant else
        f"""
            SELECT OPERATION, SQL_REDO, SCN, CSCN, COMMIT_TIMESTAMP, {redo_value_sql_clause}, {undo_value_sql_clause}
            FROM v$logmnr_contents
            WHERE table_name = :table_name AND seg_owner = :seg_owner
            AND operation IN ('INSERT', 'UPDATE', 'DELETE')
        """
    )

def add_logfiles_to_logminer(cur, logs_list, add_logmnr_sql):
    """
    Add log files to the LogMiner session.
    
    Args:
        cur (cursor): Database cursor
        logs_list (list): List of log files
        add_logmnr_sql (str): SQL statement to add log files to LogMiner
    """
    for rownum, logfilename in logs_list:
        add_logmnr_option = "new" if rownum == 1 else "addfile"
        cur.execute(add_logmnr_sql.format(add_logmnr_option), logfile=logfilename)

def prepare_stream(stream, state):
    """
    Prepare the stream for processing by extracting metadata, desired columns, and other relevant information.
    
    Args:
        stream (Stream): The stream to be prepared
        state (State): The state of the stream
    
    Returns:
        tuple: A tuple containing metadata map, desired columns, schema name, stream version, and SQL clauses for redo and undo values
    """
    md_map = metadata.to_map(stream.metadata)
    desired_columns = [c for c in stream.schema.properties.keys() if common.should_sync_column(md_map, c)]
 
    schema_name = md_map.get(()).get('schema-name')
    stream_version = get_stream_version(stream.tap_stream_id, state)
 
    redo_value_sql_clause = ",\n ".join([
        f"""DBMS_LOGMNR.MINE_VALUE(REDO_VALUE, :{idx + 1})"""
        for idx, c in enumerate(desired_columns)
    ])
 
    undo_value_sql_clause = ",\n ".join([
        f"""DBMS_LOGMNR.MINE_VALUE(UNDO_VALUE, :{idx + 1})"""
        for idx, c in enumerate(desired_columns)
    ])
 
    return md_map, desired_columns, schema_name, stream_version, redo_value_sql_clause, undo_value_sql_clause


def create_binds(schema_name, stream, desired_columns):
    """
    Create the bind variables for the mine_sql query.
    
    Args:
        schema_name (str): The schema name for the stream
        stream (Stream): The stream being processed
        desired_columns (list): List of desired columns for the stream
    
    Returns:
        list: List of bind variables
    """
    return ([
        orc_db.fully_qualified_column_name(schema_name, stream.table, c)
        for c in desired_columns
    ] + [
        orc_db.fully_qualified_column_name(schema_name, stream.table, c)
        for c in desired_columns
    ] + [stream.table] + [schema_name])


def update_state(state, stream, cscn, rows_saved):
    """
    Update the state of the stream.
    
    Args:
        state (dict): The state of the stream
        stream (Stream): The stream being processed
        cscn (int): The committed SCN
        rows_saved (int): The number of rows saved
    
    Returns:
        dict: The updated state
    """
    return singer.write_bookmark(state, stream.tap_stream_id, 'scn', int(cscn))


def create_singer_record_message(op, stream, scn, cscn, commit_ts, col_vals, columns_for_record, desired_columns, time_extracted, stream_version):
    """
    Create a Singer RecordMessage from a row returned by LogMiner.
    
    Args:
        op (str): The type of operation ('INSERT', 'UPDATE', or 'DELETE')
        stream (Stream): The stream being processed
        scn (int): The SCN
        cscn (int): The committed SCN
        commit_ts (datetime): The timestamp of the commit
        col_vals (list): List of values for the row
        columns_for_record (list): List of columns for the record
        desired_columns (list): List of original columns for the record
        time_extracted (datetime): Time when the data was extracted
        stream_version (int): The version of the stream.
    
    Returns:
        RecordMessage: A Singer RecordMessage
    """
    redo_vals = col_vals[0:len(desired_columns)]
    undo_vals = col_vals[len(desired_columns):]
    if op in ['INSERT', 'UPDATE']:
        vals = redo_vals + [cscn, None]
    elif op == 'DELETE':
        vals = undo_vals + [cscn, singer.utils.strftime(commit_ts.replace(tzinfo=pytz.UTC))]
    else:
        raise Exception("Unknown logminer operation: {}".format(op))
 
    return row_to_singer_message(stream, vals, stream_version,
                                 columns_for_record, time_extracted)


def process_logminer_rows(cur, mine_sql, binds, stream, columns_for_record, desired_columns, time_extracted, state, stream_version):
    """
    Process the rows returned by LogMiner and send the appropriate messages.
    
    Args:
        cur (cursor): Database cursor
        mine_sql (str): SQL statement for mining operations
        binds (list): List of bind variables
        stream (Stream): The stream being processed
        columns_for_record (list): List of columns for the record
        desired_columns (list): List of original columns for the record
        time_extracted (datetime): Time when the data was extracted
        state (State): The state of the stream
        stream_version (int): The version of the stream.
    
    Returns:
        tuple: A tuple containing the number of rows saved and the updated state
    """
    rows_saved = 0
    with metrics.record_counter(None) as counter:
        common.send_schema_message(stream, ['lsn'])
        LOGGER.info("Logminer sql=%s", mine_sql)
 
        for op, redo, scn, cscn, commit_ts, *col_vals in cur.execute(mine_sql, binds):
            record_message = create_singer_record_message(op, stream, scn, cscn, commit_ts, col_vals, columns_for_record, desired_columns, time_extracted, stream_version)
            singer.write_message(record_message)
            rows_saved += 1
            counter.increment()
            state = update_state(state, stream, cscn, rows_saved)
            if rows_saved % UPDATE_BOOKMARK_PERIOD == 0:
                singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))
 
    return rows_saved, state


def sync_tables_logbased(conn_config, cur, streams, state, start_scn, end_scn):
    """
    Sync tables (LOG_BASED) replication using LogMiner.
 
    Args:
        conn_config (dict): Connection configuration for the Oracle instance
        cur (cursor): Database cursor
        streams (list): List of streams to sync
        state (State): The state of the streams
        start_scn (int): Starting SCN for LogMiner
        end_scn (int): Ending SCN for LogMiner
 
    Returns:
        tuple: A tuple containing the updated state and a boolean indicating if any rows were saved
    """
    time_extracted = utils.now()
 
    LOGGER.info("Logbased (logminer) sync started for %s: %s -> %s", list(map(lambda s: s.tap_stream_id, streams)), start_scn, end_scn)
 
    logs_list_sql, add_logmnr_sql, start_logmnr_sql = generate_logmnr_sqls(start_scn, end_scn)
    LOGGER.info("%s", logs_list_sql)
    logs_list = cur.execute(logs_list_sql).fetchall()
 
    add_logfiles_to_logminer(cur, logs_list, add_logmnr_sql)
    LOGGER.info("%s", start_logmnr_sql)
    cur.execute(start_logmnr_sql)
 
    total_rows_saved = 0
    for stream in streams:
        md_map, desired_columns, schema_name, stream_version, redo_value_sql_clause, undo_value_sql_clause = prepare_stream(stream, state)
        mine_sql = generate_mine_sql(conn_config['multitenant'], conn_config['pdb_name'], redo_value_sql_clause, undo_value_sql_clause)
        binds = create_binds(schema_name, stream, desired_columns)
        columns_for_record = desired_columns + ['scn', '_sdc_deleted_at']
 
        rows_saved, state = process_logminer_rows(cur, mine_sql, binds, stream, columns_for_record, desired_columns, time_extracted, state, stream_version)
        if rows_saved > 0:
            last_cscn = singer.get_bookmark(state, stream.tap_stream_id, 'scn')
            LOGGER.info("Bookmark updated for stream %s, to end_scn %s", stream.tap_stream_id, last_cscn)
            state = singer.write_bookmark(state, stream.tap_stream_id, 'scn', last_cscn)
            singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))
 
        total_rows_saved += rows_saved
 
    return state, total_rows_saved > 0
