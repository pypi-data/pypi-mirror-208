import logging
logger = logging.getLogger(__name__)

import json

from keyrock_core import json_util

from . import exc


def catalog_diff(catalog_from, catalog_to):
    user_types = catalog_to.get('user_types', {})
    if 'schemas' in catalog_to:
        replace_user_types(catalog_to['schemas'], user_types)

    # Drop/Delete these types of items if omitted from structure_to
    explicit_group_list = ['tables', 'columns', 'constraints', 'unique']
    ignore_group_list = ['user_types']

    diff = json_util.diff(catalog_from, catalog_to, explicit_group_list=explicit_group_list, ignore_group_list=ignore_group_list)
    return diff


def replace_user_types(target_dict, user_types):
    # Search for the 'columns' subdict
    for key, val in target_dict.items():
        if key == 'columns':
            replace_user_types_on_columns(val, user_types)
        elif key == 'constraints':
            clean_up_constraints(val)
        else:
            replace_user_types(val, user_types)


def replace_user_types_on_columns(columns_dict, user_types):
    for key, val in columns_dict.items():
        # Substitute the user_type if necessary
        if 'user_type' in val:
            user_type = val['user_type']
            user_type_dict = user_types.get(user_type, {})
            del val['user_type']
            val.update(user_type_dict)

        # Convert array types and type synonyms
        col_type = val['type'].upper()
        col_size = val.get('size')
        if col_type == 'ARRAY':
            val['type'] = f"{val['element_type']}[]"
        elif col_type == 'INT':
            val['type'] = 'INTEGER'
        else:
            val['type'] = col_type

        # @todo:
        # Convert "serial" and "bigserial" types to match db representation
        # col_type = col_to.get('type')
        # if col_type == 'serial':
        #     sequence_name = "'{0}_id_seq'::regclass".format(table_name)
        #     col_to.update({
        #         'type': 'integer',
        #         'default': "nextval({0})".format(sequence_name),
        #     })
        # elif col_type == 'bigserial':
        #     sequence_name = "'{0}_id_seq'::regclass".format(table_name)
        #     col_to.update({
        #         'type': 'bigint',
        #         'default': "nextval({0})".format(sequence_name),
        #     })


def clean_up_constraints(constraints_dict):
    for key, val in constraints_dict.items():
        if key == 'primary':
            if not isinstance(val, list):
                constraints_dict[key] = [val]
        if key == 'unique':
            for uq_key_name, uq_key_cols in val.items():
                if not isinstance(uq_key_cols, list):
                    val[uq_key_name] = [uq_key_cols]
