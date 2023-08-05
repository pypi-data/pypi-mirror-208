import json
import logging

from keyrock_core import json_util
from .. import psql

logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)


default_user_types = {
    "user_types": {
        "float": {
            "type": "real"
        },
        "varchar": {
            "type": "character varying"
        },
        "id": {
            "type": "bigint",
            "is_identity": True,
            "identity_start": 100000
        },
        "id_ref": {
            "type": "bigint",
            "allow_null": True
        },
        "hash_key": {
            "type": "character varying",
            "size": 64
        }
    }
}


class Migrator():
    def __init__(self, db_config):
        self.db_config = db_config

    def provision(self) -> bool:
        logger.info(f"Migrator.provision")
        try:
            target_schema = {
                'schemas': {
                    self.db_config['schema']: {}
                }
            }
            self.update(target_schema)
        except e as Exception:
            logger.error(str(e))
            return False
        return True

    def update(self, target_schema, use_default_user_types=True):
        logger.info(f"Migrator.update")
        if use_default_user_types:
            logger.info(f"applying default types")
            new_target_schema = default_user_types.copy()
            json_util.deep_update(new_target_schema, target_schema)
            target_schema = new_target_schema

        logger.info(f"wait for psql server: {self.db_config['host']}")
        psql.wait_for_server(self.db_config, timeout_sec=15)

        debug_db_name = f"{self.db_config['host']}:{self.db_config['db']}"
        if psql.database_exists(self.db_config):
            logger.info(f"database exists: {debug_db_name}")
        else:
            logger.info(f"database doesn't exist: {debug_db_name}")
            logger.info(f"creating database: {debug_db_name}")
            psql.create_database(self.db_config)

        #logger.debug("target_schema:")
        #logger.debug(json.dumps(target_schema, indent=2))

        conn = psql.Connection(self.db_config)
        current_schema = psql.get_structure(conn)

        structure_diff = psql.catalog_diff(current_schema, target_schema)
        if structure_diff['op'] is not None:
            logger.debug("changes applied:")
            logger.debug(json.dumps(json_util.strip_unchanged(structure_diff), indent=2))

        cmd_list = psql.diff_to_cmd_list(structure_diff)
        if len(cmd_list) > 0:
            logger.debug("command list:")
            logger.debug(json.dumps(cmd_list, indent=2))

        success = True
        error_list = conn.exec_cmd_list(cmd_list)
        if len(error_list) > 0:
            success = False
            logger.error("errors encountered:")
            logger.error(json.dumps(error_list, indent=2))

        #
        # Verify that the new structure matches the intended target
        #
        updated_schema = psql.get_structure(conn)
        verify_diff = psql.catalog_diff(updated_schema, target_schema)
        if verify_diff['op'] is not None:
            success = False
            logger.error(f"target schema not completely applied:")
            logger.error(json.dumps(json_util.strip_unchanged(verify_diff), indent=2))

        verify_cmd_list = psql.diff_to_cmd_list(verify_diff)
        if len(verify_cmd_list) > 0:
            success = False
            logger.error(f"delta command list is not empty:")
            logger.error(json.dumps(verify_cmd_list, indent=2))

        return {
            'success': success,
            'error_list': error_list,
            #'structure_diff': structure_diff,
            'cmd_list': cmd_list,
            'verify_cmd_list': verify_cmd_list
        }
