import psycopg2
import marshmallow as m

import time
import json

from collections import OrderedDict
from functools import wraps
import inspect

from keyrock_core import sql_util, hash_util

from . import util
from . import cursor
from . import exc

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handle_commit(f):
    @wraps(f)
    def wrapper(self, *args, **kw):
        # If the function has a default value for commit, use it (if not explicitly set)
        signature = inspect.signature(f)
        commit = kw.get('commit', signature.parameters.get('commit'))

        reenable_autocommit = False
        if self.autocommit and commit is False:
            self.conn.autocommit = False
            reenable_autocommit = True

        return_val = f(self, *args, **kw)

        if commit and not self.autocommit:
            self.conn.commit()

        if reenable_autocommit:
            self.conn.autocommit = True

        return return_val
    return wrapper


class Connection():
    class ConfigSchema(m.Schema):
        class Meta:
            include = {
                'type': m.fields.String(missing='postgres'),
                'host': m.fields.String(missing='localhost'),
                'port': m.fields.Integer(missing=5432),
                'db': m.fields.String(missing=None),
                'user': m.fields.String(missing=None),
                'pass': m.fields.String(missing=None),
                'schema': m.fields.String(missing=None),
            }

    def  __init__(self, config=None, autocommit=False):
        self.conn = None
        self.autocommit = autocommit

        self.config = self.ConfigSchema().load(config)
        self.config_hash = hash_util.get_dict_hash(self.config)
        self.connect()

    def __del__(self):
        self.disconnect()

    def connect(self):
        if self.conn:
            logger.warning('Connection::connect: already connected')
            self.disconnect()

        conn_str = 'host={host} port={port} dbname={db} user={user} password={pass}'.format(**self.config)
        if self.config['schema']:
            options = '-c search_path={schema}'.format(**self.config)
        else:
            options = None

        try:
            self.conn = psycopg2.connect(
                conn_str,
                cursor_factory=cursor.OrderedDictCursor,
                options=options
            )
            self.conn.autocommit = self.autocommit
        except psycopg2.OperationalError as e:
            error_str = str(e)
            if 'does not exist' in error_str:
                raise exc.DatabaseDoesNotExist(self.config)
            else:
                raise e
        except Exception as e:
            error_str = str(e)
            logger.error(f'Error: {error_str}')
            raise e

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def query(self, query_str, limit=None):
        with self.conn.cursor() as cursor:
            cursor.execute(query_str)
            if limit:
                if limit == 1:
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchmany(limit)
            else:
                result = cursor.fetchall()

            return result

    def get_single_result(self, query_str, col_name=None):
        query_str = sql_util.set_limit(query_str, 1)
        result = self.query(query_str, 1)
        if col_name is None:
            return result
        else:
            if result is None:
                return None
            return result.get(col_name)

    def get_list_result(self, query_str, col_name=None, limit=None):
        result = self.query(query_str, limit)
        if col_name != None:
            return [row[col_name] for row in result]
        else:
            return result

    def get_value(self, table_name, row_id, col_list=None, key='id'):
        if col_list is None:
            col_list_str = '*'
        elif isinstance(col_list, list):
            col_list_str = ','.join(col_list)
        else:
            col_list_str = col_list

        query_str = (
            f"SELECT {col_list_str}"
            f" FROM {table_name}"
            f" WHERE {util.sql_eq(key, row_id)}"
            )
        if col_list is None or isinstance(col_list, list):
            # Return a dict value
            return self.get_single_result(query_str)
        else:
            # Return the single value (col_list is a column name, not a list)
            return self.get_single_result(query_str, col_list)

    @handle_commit
    def cmd(self, cmd, commit=None):
        with self.conn.cursor() as cursor:
            cursor.execute(cmd)

    @handle_commit
    def exec_cmd_list(self, cmd_list, commit=True):
        error_list = []
        with self.conn.cursor() as cursor:
            for cmd_str in cmd_list:
                try:
                    logger.debug(cmd_str)
                    cursor.execute(cmd_str)
                except Exception as e:
                    logger.error(e)
                    error_list.append(str(e))
        return error_list

    @handle_commit
    def insert(self, table_name, row_data, key='id', commit=True):
        if row_data is None:
            cmd_str = f"INSERT INTO {table_name} DEFAULT VALUES RETURNING {key}"
        else:
            columns_str = ', '.join([col for col, val in row_data.items()])
            values_str = ', '.join([util.to_sql(val) for col, val in row_data.items()])
            cmd_str = (
                f"INSERT INTO {table_name} ({columns_str})"
                f" VALUES ({values_str}) RETURNING {key}"
            )

        cursor = self.conn.cursor()
        cursor.execute(cmd_str)
        id = cursor.fetchone()[key]

        return id

    @handle_commit
    def insert_list(self, table_name, list_data, key='id', commit=True):
        id_list = []
        for row_data in list_data:
            #id = self.insert(table_name, row_data, key, commit=False)
            if row_data is None:
                cmd_str = f"INSERT INTO {table_name} DEFAULT VALUES RETURNING {key}"
            else:
                columns_str = ', '.join([col for col, val in row_data.items()])
                values_str = ', '.join([util.to_sql(val) for col, val in row_data.items()])
                cmd_str = (
                    f"INSERT INTO {table_name} ({columns_str})"
                    f" VALUES ({values_str}) RETURNING {key}"
                )

            cursor = self.conn.cursor()
            cursor.execute(cmd_str)
            id = cursor.fetchone()[key]
            id_list.append(id)
        return id_list

    @handle_commit
    def update(self, table_name, row_data, id=None, key='id', commit=True):
        if id is None:
            row_data = row_data.copy()
            id = row_data[key]
            del row_data[key]

        val_list = []
        for col, val in row_data.items():
            val_list.append(f"{col}={util.to_sql(val)}")
        val_list_str = ', '.join(val_list)

        cmd_str = (
            f"UPDATE {table_name}"
            f" SET {val_list_str}"
            f" WHERE {util.sql_eq(key, id)}"
            f" RETURNING {key}"
        )

        cursor = self.conn.cursor()
        cursor.execute(cmd_str)
        id = cursor.fetchone()[key]

        return id

    def upsert(self, table_name, row_data, id=None, key='id', commit=True):
        ''' e.g:
            INSERT INTO customers (name, email)
            VALUES('Microsoft', 'hotline@microsoft.com') 
            ON CONFLICT (name) 
            DO 
               UPDATE SET email = EXCLUDED.email || ';' || customers.email;
        '''
        # Using query + cmd (rather than INSERT ... ON CONFLICT)
        #  for simplicity

        if id is None and key in row_data:
            id = row_data[key]

        query_str = f"SELECT 1 AS EXISTS FROM {table_name} WHERE {util.sql_eq(key, id)} LIMIT 1"
        result = self.query(query_str, 1)

        if result is not None:
            return self.update(table_name, row_data, id, key, commit)
        else:
            if key in row_data:
                local_data = row_data
            else:
                local_data = row_data.copy()
                local_data.update({key: id})
            return self.insert(table_name, local_data, key, commit)

    @handle_commit
    def delete(self, table_name, id_list, key='id', commit=True):
        if not isinstance(id_list, list):
            id_list = [id_list]

        delete_count = 0
        with self.conn.cursor() as cursor:
            for id in id_list:
                del_str = f"DELETE FROM {table_name} WHERE {util.sql_eq(key, id)} RETURNING {key}"
                cmd_str = f"WITH del_cmd AS ({del_str}) SELECT COUNT(1) AS dc FROM del_cmd"
                cursor.execute(cmd_str)
                delete_count += cursor.fetchone()['dc']

        return delete_count

    def commit(self):
        self.conn.commit()
