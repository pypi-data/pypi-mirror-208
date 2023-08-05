from collections import OrderedDict
import json
import time

import psycopg2

from keyrock_core import json_util

from . import util
from . import exc
from .connection import Connection

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def wait_for_server(config, timeout_sec=30, interval_sec=5):
    logger.debug(f'wait_for_server timeout:{timeout_sec} interval: {interval_sec}')

    assert(interval_sec >= 0)
    assert(timeout_sec >= 0)

    waited_sec = 0
    try_count = 0
    while True:
        try_count += 1
        if is_server_ready(config):
            logger.debug(f'wait_for_server succeeded after {waited_sec} seconds and {try_count} tries')
            return True
        else:
            if waited_sec > timeout_sec:
                raise Exception(f'server is not ready after {waited_sec} seconds and {try_count} tries')
            else:
                logger.debug(f'wait_for_server will retry in {interval_sec} seconds')
                time.sleep(interval_sec)
                waited_sec += interval_sec
    raise


def is_server_ready(config):
    config = Connection.ConfigSchema().load(config)
    logger.debug(f'is_server_ready')

    # Create a temp config for the root "postgres" database
    root_config = config.copy()
    root_config['db'] = 'postgres'

    try:
        conn = Connection(config)
    except exc.DatabaseDoesNotExist as e:
        logger.info(f'server is ready: {str(e)}')
        return True
    except Exception as e:
        logger.info(f'server is not ready: {str(e)}')
        return False

    logger.info(f'server is ready')
    return True


def database_exists(config):
    try:
        conn = Connection(config)
    except exc.DatabaseDoesNotExist:
        return False
    return True


def create_database(config):
    config = Connection.ConfigSchema().load(config)

    db_name = config['db']
    create_cmd = f'CREATE DATABASE {db_name}'

    # Create a temp config for the root "postgres" database
    root_config = config.copy()
    root_config['db'] = 'postgres'

    conn = Connection(root_config, autocommit=True)
    conn.cmd(create_cmd)


def drop_database(config):
    config = Connection.ConfigSchema().load(config)

    db_name = config['db']
    drop_cmd = f'DROP DATABASE {db_name}'

    # Create a temp config for the root "postgres" database
    root_config = config.copy()
    root_config['db'] = 'postgres'

    conn = Connection(root_config, autocommit=True)
    conn.cmd(drop_cmd)


def get_structure(conn):
    db_info = conn.get_single_result(
        "SELECT"
        " current_catalog AS catalog,"
        " current_user AS user"
        #" current_schemas(FALSE) AS schemas,"
    )
    logger.debug('DB INFO:')
    logger.debug(json.dumps(db_info, indent=2))

    # Catalog is the root element (can be only one per connection)
    catalog = {}
    catalog['schemas'] = get_schemas(conn)

    return catalog


def get_schemas(conn):
    schemas = {}
    schema_query = (
        "SELECT * FROM information_schema.schemata"
        " WHERE TRUE"
        #f" AND schema_owner = '{db_info['user']}'"
        # Exclude system schemas:
        " AND schema_name NOT LIKE 'pg_%'"
        " AND schema_name != 'information_schema'"
        " ORDER BY schema_name ASC"
    )
    schema_list = conn.get_list_result(schema_query, 'schema_name')

    for schema_name in schema_list:
        schema = schemas.setdefault(schema_name, {})
        schema['tables'] = get_tables(conn, schema_name)

    return schemas


def get_tables(conn, schema_name):
    tables = {}
    table_query = (
        "SELECT * FROM information_schema.tables"
        f" WHERE table_schema = '{schema_name}'"
        " ORDER BY table_name ASC"
    )
    table_list = conn.get_list_result(table_query, 'table_name')

    for table_name in table_list:
        table = tables.setdefault(table_name, {})
        table['columns'] = get_columns(conn, schema_name, table_name)
        table['constraints'] = get_constraints(conn, schema_name, table_name)

    return tables


def get_columns(conn, schema_name, table_name):
    columns = {}
    columns_query = (
        "SELECT"
        "    c.column_name, c.data_type, c.character_maximum_length, c.is_nullable"
        "  , c.column_default, c.ordinal_position"
        "  , c.is_identity, c.identity_start, c.identity_increment"
        "  , e.data_type AS element_type"
        " FROM information_schema.columns c"
        " LEFT JOIN information_schema.element_types e"
        "  ON (c.table_catalog, c.table_schema, c.table_name, 'TABLE', c.dtd_identifier)"
        "   = (e.object_catalog, e.object_schema, e.object_name, e.object_type, e.collection_type_identifier)"    
        f" WHERE c.table_schema = '{schema_name}'"
        f" AND c.table_name = '{table_name}'"
    )
    column_list = conn.get_list_result(columns_query)

    for column_src in column_list:
        column_name = column_src['column_name']
        columns[column_name] = {
            'is_identity': (column_src['is_identity'] == 'YES'),
            'identity_start': column_src['identity_start'],
            'identity_increment': column_src['identity_increment'],
            'type': column_src['data_type'].upper(),
            'size': column_src['character_maximum_length'],
            'allow_null': (column_src['is_nullable'] == 'YES'),
            'default': util.convert_default(column_src['column_default']),
            'pos': column_src['ordinal_position'],
            'element_type': column_src['element_type'],
        }

    return columns


def get_constraints(conn, schema_name, table_name):
    constraints = {}
    constraints_query = (
        "SELECT"
        "    constraint_name, constraint_type"
        " FROM information_schema.table_constraints"
        f" WHERE table_schema = '{schema_name}'"
        f" AND table_name = '{table_name}'"
    )
    constraint_list = conn.get_list_result(constraints_query)
    #print('CONSTRAINTS', json.dumps(constraint_list, indent=2))

    for constraint_src in constraint_list:
        constraint_name = constraint_src['constraint_name']
        constraint_type = constraint_src['constraint_type'].upper()

        columns_query = (
            "SELECT"
            "    table_name, column_name"
            " FROM information_schema.key_column_usage"
            f" WHERE table_schema = '{schema_name}'"
            f" AND constraint_name = '{constraint_name}'"
        )
        column_list = conn.get_list_result(columns_query)
        #print('CONSTRAINT', constraint_name, constraint_type)
        #print('CONSTRAINT COLUMNS', json.dumps(column_list, indent=2))

        if constraint_type == 'FOREIGN KEY':
            foreign_keys = constraints.setdefault('foreign', {})
            (local_col, foreign_path) = get_foreign_constraint(conn, schema_name, table_name, constraint_name)
            foreign_keys[local_col] = foreign_path
        elif constraint_type == 'PRIMARY KEY':
            constraints['primary'] = [ c['column_name'] for c in column_list ]
        elif constraint_type == 'UNIQUE':
            # Strip out table_name prefix on unique keys
            prefix = f'{table_name}_'
            if constraint_name.startswith(prefix):
                constraint_name = constraint_name[len(prefix):]
            unique_keys = constraints.setdefault('unique', {})
            unique_keys[constraint_name] = [ c['column_name'] for c in column_list ]
        elif constraint_type == 'CHECK':
            # not-null check
            pass
        else:
            logger.warning(f"Unhandled constraint type: '{constraint_type}' for '{constraint_name}")

    return constraints


def get_foreign_constraint(conn, schema_name, table_name, constraint_name):
    columns_query = (
        "SELECT"
        "    cu.table_name AS foreign_table_name,"
        "    cu.column_name AS foreign_column_name,"
        "    ku.table_name AS local_table_name,"
        "    ku.column_name AS local_column_name"
        " FROM information_schema.constraint_column_usage cu"
        " LEFT JOIN information_schema.key_column_usage ku"
        "  ON (cu.table_schema, cu.constraint_name)"
        "   = (ku.table_schema, ku.constraint_name)"
        f" WHERE cu.table_schema = '{schema_name}'"
        f" AND cu.constraint_name = '{constraint_name}'"
    )
    column_map = conn.get_single_result(columns_query)

    local_column_name = column_map['local_column_name']
    foreign_target = f"{column_map['foreign_table_name']}.{column_map['foreign_column_name']}"

    return (local_column_name, foreign_target)
