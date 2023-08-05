import logging
logger = logging.getLogger(__name__)

import json
import psycopg2


def to_sql(value):
    ''' For manually setting values '''
    if value is None:
        return 'NULL'
    if value == 'null':
        return 'NULL'

    if isinstance(value, dict):
        return "'{}'".format(json.dumps(value).replace("'", "''"))

    if isinstance(value, list):
        assert(False)

    if isinstance(value, psycopg2.extensions.Binary):
        return value

    if value is True:
        return 'TRUE'
    if value is False:
        return 'FALSE'

    if value == 'CURRENT_TIMESTAMP':
        return value

    # Escape single quotes in strings
    str_value = "'{}'".format(str(value).replace("'", "''"))
    return str_value


def convert_default(str_val):
    ''' For reading in default values from the db '''
    if str_val is None:
        return None
    str_lower = str_val.lower()
    if str_lower == 'null':
        return None
    if str_lower.startswith('null::'):
        return None
    if str_lower == 'false':
        return False
    if str_lower == 'true':
        return True
    return str_val


def sql_eq(col_name, value):
    if value is None:
        return f"{col_name} IS NULL"
    else:
        return f"{col_name}={to_sql(value)}"


def sql_binary(data):
    return psycopg2.Binary(data)
