import unittest

import os
import json

try:
    import psycopg2
except:
    psycopg2 = None

from keyrock_core import config_loader
from keyrock_core import json_util

from . import *

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '.'))


class TestMigration(unittest.TestCase):
    config = {
        'host': 'pg',
        'port': 5432,
        'db': 'migration_test',
        'user': 'postgres',
        'pass': 'postgres',
    }

    @classmethod
    def setUpClass(cls):
        if psycopg2 is None:
            raise unittest.SkipTest('psycopg2 not installed')

        wait_for_server(cls.config, timeout_sec=15)

        if database_exists(cls.config):
            logger.warning(f'Test database already exists: {cls.config}')
            drop_database(cls.config)

        try:
            create_database(cls.config)
        except Exception as e:
            cls.tearDownClass()
            raise e

    @classmethod
    def tearDownClass(cls):
        assert (database_exists(cls.config)), 'database does not exist'

        # Remove the test database
        drop_database(cls.config)

    def setUp(self):
        self.assertTrue(database_exists(self.config), 'database does not exist')
        self.conn = Connection(self.config)

    def test_root(self):
        try:
            self.run_migration('test_data/unit_test_init.yml')
            self.run_migration('test_data/unit_test_2.yml')
            # @todo: Load some test data and run more migrations
        except Exception as e:
            logger.error(str(e))
            self.conn.disconnect()
            raise e

    def run_migration(self, target_config_file):
        logger.debug(f'run migration: {target_config_file}')

        current_structure = get_structure(self.conn)
        #logger.debug('current_structure')
        #logger.debug(json.dumps(current_structure, indent=2))

        target_structure = config_loader.load(os.path.join(ROOT_DIR, target_config_file))
        #logger.debug('target_structure:')
        #logger.debug(json.dumps(target_structure, indent=2))

        structure_diff = catalog_diff(current_structure, target_structure)
        logger.debug('structure_diff (changes only):')
        logger.debug(json.dumps(json_util.strip_unchanged(structure_diff), indent=2))

        cmd_list = diff_to_cmd_list(structure_diff)
        logger.debug('cmd_list:')
        logger.debug(json.dumps(cmd_list, indent=2))

        error_list = self.conn.exec_cmd_list(cmd_list)
        logger.debug('error_list:')
        logger.debug(json.dumps(error_list, indent=2))
        self.assertEqual(len(error_list), 0)

        #
        # Verify that the new structure matches the target
        #
        updated_structure = get_structure(self.conn)
        verify_diff = catalog_diff(updated_structure, target_structure)
        logger.debug('verify_diff (should have no changes):')
        logger.debug(json.dumps(json_util.strip_unchanged(verify_diff), indent=2))
        self.assertEqual(verify_diff['op'], None)

        cmd_list = diff_to_cmd_list(verify_diff)
        logger.debug('re-apply cmd list (should be empty):')
        logger.debug(json.dumps(cmd_list, indent=2))
        self.assertEqual(len(cmd_list), 0)


class TestPsql(unittest.TestCase):
    config = {
        'host': 'pg',
        'port': 5432,
        'db': 'operations_test',
        'schema': 'test_schema',
        'user': 'postgres',
        'pass': 'postgres',
    }

    target_config_file = 'test_data/op_test_init.yml'

    @classmethod
    def setUpClass(cls):
        if psycopg2 is None:
            raise unittest.SkipTest('psycopg2 not installed')

        wait_for_server(cls.config, timeout_sec=15)

        if database_exists(cls.config):
            logger.warning(f'Test database already exists: {cls.config}')
            drop_database(cls.config)

        #
        # Set up the initial structure
        #
        try:
            create_database(cls.config)
            conn = Connection(cls.config)
            current_structure = get_structure(conn)
            target_structure = config_loader.load(os.path.join(ROOT_DIR, cls.target_config_file))
            structure_diff = catalog_diff(current_structure, target_structure)
            cmd_list = diff_to_cmd_list(structure_diff)
            error_list = conn.exec_cmd_list(cmd_list)
        except Exception as e:
            cls.tearDownClass()
            raise e

    @classmethod
    def tearDownClass(cls):
        assert (database_exists(cls.config)), 'database does not exist'

        # Remove the test database
        drop_database(cls.config)

    def setUp(self):
        self.assertTrue(database_exists(self.config), 'database does not exist')
        self.conn = Connection(self.config, autocommit=True)

    def tearDown(self):
        if self.conn:
            self.conn.disconnect()

    def test_basic_ops(self):
        self.conn.cmd("DELETE FROM test_table_a")

        for test_val in [11, 12, 13]:
            row_id = self.conn.insert('test_table_a', {'int_column': test_val})
            query_str = f"SELECT int_column FROM test_table_a WHERE {util.sql_eq('id', row_id)}"
            result = self.conn.get_single_result(query_str, 'int_column')
            self.assertEqual(result, test_val)

            test_id = self.conn.update('test_table_a', {'int_column': test_val+1}, row_id)
            self.assertEqual(test_id, row_id)

            result = self.conn.get_value('test_table_a', row_id)
            self.assertEqual(result['int_column'], test_val+1)

            result = self.conn.get_value('test_table_a', row_id, ['int_column'])
            self.assertEqual(result['int_column'], test_val+1)

            result = self.conn.get_value('test_table_a', row_id, 'int_column')
            self.assertEqual(result, test_val+1)

        query_str = "SELECT * FROM test_table_a LIMIT 2"
        result = self.conn.get_list_result(query_str)
        self.assertEqual(len(result), 2)

        test_id = self.conn.insert('test_table_a', {'int_column': 69})
        delete_count = self.conn.delete('test_table_a', test_id)
        self.assertEqual(delete_count, 1)

        delete_count = self.conn.delete('test_table_a', None, key='str_column_opt')
        query_str = "SELECT COUNT(1) AS row_count FROM test_table_a"
        result = self.conn.get_single_result(query_str)
        self.assertEqual(result['row_count'], 0)

    def test_upsert(self):
        self.conn.cmd("DELETE FROM test_table_b")

        test_id = self.conn.upsert('test_table_b', {'str_column': 'abc'}, id='testkeyvalue', key='test_key')
        self.assertEqual(test_id, 'testkeyvalue')

        test_id = self.conn.upsert('test_table_b', {'str_column': 'def', 'test_key': 'testkeyvalue'}, key='test_key')
        self.assertEqual(test_id, 'testkeyvalue')

        test_id = self.conn.upsert('test_table_b', {'str_column': 'ghi', 'test_key': 'newkeyvalue'}, id='testkeyvalue', key='test_key')
        self.assertEqual(test_id, 'newkeyvalue')

        test_id = self.conn.upsert('test_table_b', {'str_column': 'new', 'test_key': 'insertkeyvalue'}, id='testkeyvalue', key='test_key')
        self.assertEqual(test_id, 'insertkeyvalue')

        id_list = ['insertkeyvalue', 'newkeyvalue']
        delete_count = self.conn.delete('test_table_b', id_list, key='test_key')
        self.assertEqual(delete_count, 2)

    def test_insert_list(self):
        self.conn.cmd("DELETE FROM test_table_a")

        item_list = [
            {'int_column': 1},
            {'int_column': 2},
            {'int_column': 3},
        ]
        id_list = self.conn.insert_list('test_table_a', item_list)
        self.assertEqual(len(id_list), 3)

        delete_count = self.conn.delete('test_table_a', id_list)
        self.assertEqual(delete_count, 3)
