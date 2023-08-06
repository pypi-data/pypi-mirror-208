import re
import singer
from singer import  metadata
import decimal
import oracledb

# max decimal digits are 100 for singer
MAX_DECIMAL_DIGITS = 101


def should_sync_column(metadata, field_name):
    """Determine if a column should be synced.

    Args:
        metadata (dict): Metadata containing the properties of the column.
        field_name (str): The name of the column.

    Returns:
        bool: True if the column should be synced, False otherwise.
    """
    field_metadata = metadata.get(('properties', field_name), {})
    return singer.should_sync_field(field_metadata.get('inclusion'),
                                    field_metadata.get('selected'),
                                    True)


def send_schema_message(stream, bookmark_properties):
    """Send a schema message for the given stream.

    Args:
        stream (Stream): A singer stream object.
        bookmark_properties (list): A list of bookmark properties.
    """
    s_md = metadata.to_map(stream.metadata)
    if s_md.get((), {}).get('is-view'):
        key_properties = s_md.get((), {}).get('view-key-properties')
    else:
        key_properties = s_md.get((), {}).get('table-key-properties')

    schema_message = singer.SchemaMessage(stream=stream.stream,
                                          schema=stream.schema.to_dict(),
                                          key_properties=key_properties,
                                          bookmark_properties=bookmark_properties)
    singer.write_message(schema_message)


def row_to_singer_message(stream, row, version, columns, time_extracted):
    """Convert a row from the database to a singer message.

    Args:
        stream (Stream): A singer stream object.
        row (tuple): A tuple containing the values of a row.
        version (str): The version of the singer message.
        columns (list): A list of column names.
        time_extracted (datetime.datetime): The time the row was extracted.

    Returns:
        singer.RecordMessage: A singer message containing the row data.
    """
    row_to_persist = ()
    for idx, elem in enumerate(row):
        property_type = stream.schema.properties[columns[idx]].type
        property_format = stream.schema.properties[columns[idx]].format
        if elem is None:
            row_to_persist += (elem,)
        elif ('string' in property_type or property_type == 'string') and property_format == 'singer.decimal':
            if len(str(elem)) > MAX_DECIMAL_DIGITS:
                elem = elem.normalize()
            row_to_persist += (str(elem),)
        elif 'integer' in property_type or property_type == 'integer':
            integer_representation = int(elem)
            row_to_persist += (integer_representation,)
        else:
            row_to_persist += (elem,)

    rec = dict(zip(columns, row_to_persist))

    return singer.RecordMessage(
        stream=stream.stream,
        record=rec,
        version=version,
        time_extracted=time_extracted)

def OutputTypeHandler(cursor, name, defaultType, size, precision, scale):
    """Handle custom output types for the cursor.

    Args:
        cursor (Cursor): A database cursor.
        name (str): The name of the column.
        defaultType (int): The default type of the column.
        size (int): The size of the column.
        precision (int): The precision of the column.
        scale (int): The scale of the column.

    Returns:
        CursorVar: A cursor variable with the specified type.
    """
    if defaultType == oracledb.NUMBER:
        return cursor.var(decimal.Decimal, arraysize = cursor.arraysize)


def prepare_columns_sql(stream, c):
    """Prepare the SQL for a column.

    Args:
        stream (Stream): A singer stream object.

        c (str): The name of the column.

    Returns:
        str: The formatted SQL string for the column.
    """
    column_name = f""" "{c}" """
    if 'string' in stream.schema.properties[c].type and stream.schema.properties[c].format == 'date-time':
        return f"to_char({column_name})"

    return column_name

def prepare_where_clause_arg(val, sql_datatype):
    """Format the argument for a WHERE clause based on the SQL data type.

    Args:
        val (str): The value to be used in the WHERE clause.
        sql_datatype (str): The SQL data type of the value.

    Returns:
        str: The formatted value for the WHERE clause.
    """
    if sql_datatype == 'NUMBER':
        return val
    elif sql_datatype == 'DATE':
        return f"to_date('{val}')"
    elif re.search('TIMESTAMP\([0-9]\) WITH (LOCAL )?TIME ZONE', sql_datatype):
        return f"to_timestamp_tz('{val}')"
    elif re.search('TIMESTAMP\([0-9]\)', sql_datatype):
        return f"to_timestamp('{val}')"
    else:
        return f"'{val}'"
