#!/usr/bin/env python3
import singer
from singer import utils
import singer.metadata as metadata
import macrometa_source_oracle.connection as orc_db
import macrometa_source_oracle.sync_strategies.common as common
import singer.metrics as metrics
import copy
import time

LOGGER = singer.get_logger()

UPDATE_BOOKMARK_PERIOD = 1000


def set_session_parameters(cursor, conn_config):
   """Set session parameters for the Oracle connection."""
   cursor.execute("ALTER SESSION SET TIME_ZONE = '00:00'")
   if conn_config['multitenant']:
       cursor.execute(f"ALTER SESSION SET CONTAINER = {conn_config['pdb_name']}")  # PDB
   cursor.execute("""ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD"T"HH24:MI:SS."00+00:00"'""")
   cursor.execute("""ALTER SESSION SET NLS_TIMESTAMP_FORMAT='YYYY-MM-DD"T"HH24:MI:SSXFF"+00:00"'""")
   cursor.execute("""ALTER SESSION SET NLS_TIMESTAMP_TZ_FORMAT  = 'YYYY-MM-DD"T"HH24:MI:SS.FFTZH:TZM'""")


def get_stream_version(state, stream):
   """Get stream version based on state."""
   if singer.get_bookmark(state, stream.tap_stream_id, 'ORA_ROWSCN') is None:
       return int(time.time() * 1000)
   else:
       return singer.get_bookmark(state, stream.tap_stream_id, 'version')


def update_state_version(state, stream, stream_version):
   """Update state with the stream version."""
   return singer.write_bookmark(state, stream.tap_stream_id, 'version', stream_version)


def get_activate_version_message(stream, stream_version):
   """Get ActivateVersionMessage for the given stream and version."""
   return singer.ActivateVersionMessage(stream=stream.stream, version=stream_version)


def execute_select(cursor, select_sql):
   """Execute the select query and log it."""
   LOGGER.info("Query: %s", select_sql)
   return cursor.execute(select_sql)


def sync_view_or_table(conn_config, stream, state, desired_columns, is_view):
   """
   Sync view or table based on the is_view flag.

   :param conn_config: Connection configuration
   :param stream: Stream to sync
   :param state: State of the tap
   :param desired_columns: Desired columns for the sync
   :param is_view: Boolean flag, True if syncing a view, False if syncing a table
   :return: Updated state
   """
   connection = orc_db.open_connection(conn_config)
   connection.outputtypehandler = common.OutputTypeHandler

   cursor = connection.cursor()
   set_session_parameters(cursor, conn_config)
   time_extracted = utils.now()

   first_run = singer.get_bookmark(state, stream.tap_stream_id, 'version') is None
   stream_version = get_stream_version(state, stream)
   state = update_state_version(state, stream, stream_version)

   md = metadata.to_map(stream.metadata)
   schema_name = md.get(()).get('schema-name')

   escaped_columns = [common.prepare_columns_sql(stream, c) for c in desired_columns]
   escaped_schema = schema_name
   escaped_table = stream.table
   activate_version_message = get_activate_version_message(stream, stream_version)

   if first_run:
       singer.write_message(activate_version_message)

   with metrics.record_counter(None) as counter:
      if is_view:
         select_sql = f"SELECT {','.join(escaped_columns)} FROM {escaped_schema}.{escaped_table}"
      else:
         ora_rowscn = singer.get_bookmark(state, stream.tap_stream_id, 'ORA_ROWSCN')
         select_sql = (
             None if is_view else
             f"""SELECT {','.join(escaped_columns)}{', ORA_ROWSCN' if ora_rowscn else ''}
                            FROM {escaped_schema}.{escaped_table}
                            {f'WHERE ORA_ROWSCN >= {str(ora_rowscn)}' if ora_rowscn else ''}
                            ORDER BY ORA_ROWSCN ASC"""
         )

      rows_saved = 0
      for row in execute_select(cursor, select_sql):
          ora_rowscn = None
          if not is_view:
              ora_rowscn = row[-1]
              row = row[:-1]

          record_message = common.row_to_singer_message(stream, row, stream_version, desired_columns, time_extracted)
          singer.write_message(record_message)

          if not is_view:
              state = singer.write_bookmark(state, stream.tap_stream_id, 'ORA_ROWSCN', ora_rowscn)
              rows_saved += 1
              if rows_saved % UPDATE_BOOKMARK_PERIOD == 0:
                  singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

          counter.increment()

   if not is_view:
       state = singer.write_bookmark(state, stream.tap_stream_id, 'ORA_ROWSCN', None)

   singer.write_message(activate_version_message)
   cursor.close()
   connection.close()

   return state


def sync_view(conn_config, stream, state, desired_columns):
   return sync_view_or_table(conn_config, stream, state, desired_columns, is_view=True)


def sync_table(conn_config, stream, state, desired_columns):
   return sync_view_or_table(conn_config, stream, state, desired_columns, is_view=False)
