import json

from keyrock_core import json_util

from . import exc
from . import util

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def diff_to_cmd_list(node, cmd_list=None, context=None):
    if cmd_list is None:
        cmd_list = []

    if context is None:
        context = {}

    if node['op'] is None:
        return cmd_list

    if node['op'] == 'dict':
        for group_key, group_node in node['diff'].items():
            cmd_gen = CmdGen.get_cmd_gen(group_key)
            if cmd_gen is not None:
                cmd_gen.parse_diff(group_node, cmd_list, context)
    return cmd_list


class CmdGen():
    group_map = {}

    @staticmethod
    def register_cmd_gen(group_key, context_key, cmd_gen_class):
        CmdGen.group_map[group_key] = cmd_gen_class(context_key)

    @staticmethod
    def get_cmd_gen(group_key):
        cmd_gen_instance = CmdGen.group_map.get(group_key)
        if cmd_gen_instance is None:
            logger.debug(f'cmd_gen_class not registered for: {group_key}')
            return None
        return cmd_gen_instance

    def __init__(self, context_key):
        self.context_key = context_key

    def parse_diff(self, group_node, cmd_list, context):
        group_op = group_node['op']
        if group_op == 'dict':
            for item_key, item_node in group_node['diff'].items():
                self.write(item_key, item_node, cmd_list, context)
        elif group_op == 'add':
            raise NotImplementedError('group add not implemented')
        elif group_op == 'del':
            raise NotImplementedError('group del not implemented')

    def update_context(self, item_key, context):
        context[self.context_key] = item_key

    def write(self, item_key, item_node, cmd_list, context):
        op = item_node['op']
        if op == 'dict':
            return self.write_dict(item_key, item_node['diff'], cmd_list, context)
        if op == 'add':
            return self.write_add(item_key, item_node['val'], cmd_list, context)
        if op == 'del':
            return self.write_del(item_key, item_node['val_from'], cmd_list, context)
        if op == 'mod':
            return self.write_mod(item_key, item_node['val_from'], item_node['val'], cmd_list, context)
        if op is None:
            return None
        assert(False), f"unrecognized op: {op}"

    def write_dict(self, item_key, item_node, cmd_list, context):
        logger.debug(f"write_dict for {self.context_key}: {item_key}")
        self.update_context(item_key, context)
        for group_key, group_node in item_node.items():
            cmd_gen = CmdGen.get_cmd_gen(group_key)
            if cmd_gen is not None:
                cmd_gen.parse_diff(group_node, cmd_list, context)

    def write_mod(self, item_key, item_data_from, item_data, cmd_list, context):
        logger.debug(f"write_mod for {self.context_key}: {item_key} {item_data_from} -> {item_data}")
        self.update_context(item_key, context)

    def write_add(self, item_key, item_data, cmd_list, context):
        logger.debug(f"write_add for {self.context_key}: {item_key} {item_data}")
        self.update_context(item_key, context)

    def add_child_data(self, group_key, item_data, cmd_list, context):
        if item_data is not None:
            if group_key in item_data:
                group_data = item_data[group_key]
                cmd_gen = CmdGen.get_cmd_gen(group_key)
                for sub_item_key, sub_item_data in group_data.items():
                    cmd_gen.write_add(sub_item_key, sub_item_data, cmd_list, context)

    def write_del(self, item_key, item_data, cmd_list, context):
        logger.debug(f"write_del for {self.context_key}")


class CatalogCmdGen(CmdGen):
    pass

CmdGen.register_cmd_gen('catalogs', 'catalog', CatalogCmdGen)


class SchemaCmdGen(CmdGen):
    def write_add(self, item_key, item_data, cmd_list, context):
        cmd_list.append(f"CREATE SCHEMA {item_key} AUTHORIZATION CURRENT_USER")
        super().write_add(item_key, item_data, cmd_list, context)
        self.add_child_data('tables', item_data, cmd_list, context)

    def write_del(self, item_key, item_data, cmd_list, context):
        cmd_list.append(f"DROP SCHEMA {item_key}")
        super().write_del(item_key, item_data, cmd_list, context)

CmdGen.register_cmd_gen('schemas', 'schema', SchemaCmdGen)


class TableCmdGen(CmdGen):
    def write_add(self, item_key, item_data, cmd_list, context):
        cmd_list.append(f"CREATE TABLE {context['schema']}.{item_key} ()")
        super().write_add(item_key, item_data, cmd_list, context)
        self.add_child_data('columns', item_data, cmd_list, context)
        self.add_child_data('constraints', item_data, cmd_list, context)

    def write_del(self, item_key, item_data, cmd_list, context):
        cmd_list.append(f"DROP TABLE {context['schema']}.{item_key}")
        super().write_del(item_key, item_data, cmd_list, context)

CmdGen.register_cmd_gen('tables', 'table', TableCmdGen)


class ColumnCmdGen(CmdGen):
    def write_add(self, item_key, item_data, cmd_list, context):
        cmd_str = (
            f"ALTER TABLE {context['schema']}.{context['table']}"
            f" ADD COLUMN {item_key} {item_data['type']}"
        )

        if item_data.get('size'):
            cmd_str += f"({item_data['size']})"

        if item_data.get('is_identity'):
            identity_start = item_data.get('identity_start', 1)
            identity_method = item_data.get('identity_method', 'BY DEFAULT')
            cmd_str += f' GENERATED {identity_method} AS IDENTITY (START WITH {identity_start})'

        if not item_data.get('allow_null'):
            cmd_str += ' NOT NULL'

        if 'default' in item_data:
            default_val = util.to_sql(item_data['default'])
            cmd_str += f' DEFAULT {default_val}'
        cmd_list.append(cmd_str)
        super().write_add(item_key, item_data, cmd_list, context)

    def write_del(self, item_key, item_data, cmd_list, context):
        cmd_list.append(f"ALTER TABLE {context['schema']}.{context['table']} DROP COLUMN {item_key}")
        super().write_del(item_key, item_data, cmd_list, context)

    def write_dict(self, item_key, item_node, cmd_list, context):
        item_data = {}
        for prop_key, prop_node in item_node.items():
            if prop_node['op'] != 'del':
                prop_data = json_util.assemble_node_data(prop_node)
                item_data[prop_key] = prop_data

        # Update type (and/or size)
        type_op = json_util.get_property_op(item_node, 'type')
        size_op = json_util.get_property_op(item_node, 'size')
        if type_op is not None or size_op is not None:
            self.update_type(item_key, item_data, cmd_list, context)

        # Update identity
        # @todo: this could be cleaned up
        is_identity_op = json_util.get_property_op(item_node, 'is_identity')
        identity_start_op = json_util.get_property_op(item_node, 'identity_start')
        identity_method_op = json_util.get_property_op(item_node, 'identity_method')
        if is_identity_op is not None or identity_start_op is not None or identity_method_op is not None:
            is_identity = item_data.get('is_identity')
            if is_identity:
                identity_start = item_data.get('identity_start', 1)
                identity_method = item_data.get('identity_method', 'BY DEFAULT')
                if is_identity_op == 'mod' or is_identity_op == 'add':
                    cmd_str = (
                        f"ALTER TABLE {context['schema']}.{context['table']}"
                        f" ALTER COLUMN {item_key} ADD GENERATED {identity_method} AS IDENTITY (START WITH {identity_start})"
                    )
                    cmd_list.append(cmd_str)
                elif identity_start_op is not None:
                    cmd_str = (
                        f"ALTER TABLE {context['schema']}.{context['table']}"
                        f" ALTER COLUMN {item_key} SET GENERATED {identity_method} RESTART WITH {identity_start}"
                    )
                    cmd_list.append(cmd_str)
            else:
                cmd_str = (
                    f"ALTER TABLE {context['schema']}.{context['table']}"
                    f" ALTER COLUMN {item_key} DROP IDENTITY IF EXISTS"
                )
                cmd_list.append(cmd_str)

        # Change allow null
        allow_null_op = json_util.get_property_op(item_node, 'allow_null')
        if allow_null_op is not None:
            self.update_allow_null(item_key, item_data, cmd_list, context)

        # Change default value
        # @todo: this could be cleaned up
        default_val_op = json_util.get_property_op(item_node, 'default')
        if default_val_op == 'del':
            cmd_str = (
                f"ALTER TABLE {context['schema']}.{context['table']}"
                f" ALTER COLUMN {item_key} DROP DEFAULT"
            )
            cmd_list.append(cmd_str)
        elif default_val_op is not None:
            default_val = util.to_sql(item_data['default'])
            cmd_str = (
                f"ALTER TABLE {context['schema']}.{context['table']}"
                f" ALTER COLUMN {item_key} SET DEFAULT {default_val}"
            )
            cmd_list.append(cmd_str)

        super().write_dict(item_key, item_node, cmd_list, context)

    def update_type(self, item_key, item_data, cmd_list, context):
        cmd_str = (
            f"ALTER TABLE {context['schema']}.{context['table']}"
            f" ALTER COLUMN {item_key} TYPE {item_data['type']}"
        )
        if item_data.get('size'):
            cmd_str += f"({item_data['size']})"
        cmd_list.append(cmd_str)

    def update_allow_null(self, item_key, item_data, cmd_list, context):
        allow_null = item_data.get('allow_null')
        if allow_null:
            cmd_str = (
                f"ALTER TABLE {context['schema']}.{context['table']}"
                f" ALTER COLUMN {item_key} DROP NOT NULL"
            )
            cmd_list.append(cmd_str)
        else:
            cmd_str = (
                f"ALTER TABLE {context['schema']}.{context['table']}"
                f" ALTER COLUMN {item_key} SET NOT NULL"
            )
            cmd_list.append(cmd_str)

CmdGen.register_cmd_gen('columns', 'column', ColumnCmdGen)


class ConstraintCmdGen(CmdGen):
    def write_add(self, item_key, item_data, cmd_list, context):
        if item_key == 'primary':
            if not isinstance(item_data, list):
                item_data = [item_data]
            key_str = ', '.join(item_data)

            cmd_str = (
                f"ALTER TABLE {context['schema']}.{context['table']}"
                f" ADD PRIMARY KEY({key_str})"
            )
            cmd_list.append(cmd_str)
        else:
            cmd_gen = CmdGen.get_cmd_gen(item_key)
            for sub_key, sub_data in item_data.items():
                cmd_gen.write_add(sub_key, sub_data, cmd_list, context)

        super().write_add(item_key, item_data, cmd_list, context)

    def write_del(self, item_key, item_data, cmd_list, context):
        if item_key == 'primary':
            cmd_str = (
                f"ALTER TABLE {context['schema']}.{context['table']}"
                f" DROP CONSTRAINT IF EXISTS {context['table']}_pkey"
            )
            cmd_list.append(cmd_str)
        else:
            cmd_gen = CmdGen.get_cmd_gen(item_key)
            # Drop each of the constraints
            for sub_key, sub_data in item_node.items():
                cmd_gen.write_del(sub_key, sub_data, cmd_list, context)

        super().write_del(item_key, item_data, cmd_list, context)

    def write_mod(self, item_key, item_data_from, item_data, cmd_list, context):
        if item_key == 'primary':
            self.write_del(item_key, item_data_from, cmd_list, context)
            self.write_add(item_key, item_data, cmd_list, context)
        super().write_mod(item_key, item_data_from, item_data, cmd_list, context)

    def write_dict(self, item_key, item_node, cmd_list, context):
        if item_key == 'primary':
            pass
        else:
            cmd_gen = CmdGen.get_cmd_gen(item_key)
            for sub_key, sub_node in item_node.items():
                cmd_gen.write(sub_key, sub_node, cmd_list, context)

        super().write_dict(item_key, item_node, cmd_list, context)

CmdGen.register_cmd_gen('constraints', 'constraint', ConstraintCmdGen)


class UniqueConstraintCmdGen(CmdGen):
    def write_add(self, item_key, item_data, cmd_list, context):
        if not isinstance(item_data, list):
            item_data = [item_data]
        key_str = ', '.join(item_data)

        cmd_str = (
            f"ALTER TABLE {context['schema']}.{context['table']}"
            f" ADD CONSTRAINT {context['table']}_{item_key} UNIQUE ({key_str})"
        )
        cmd_list.append(cmd_str)
        super().write_add(item_key, item_data, cmd_list, context)

    def write_del(self, item_key, item_data, cmd_list, context):
        cmd_str = (
            f"ALTER TABLE {context['schema']}.{context['table']}"
            f" DROP CONSTRAINT IF EXISTS {context['table']}_{item_key}"
        )
        cmd_list.append(cmd_str)
        super().write_del(item_key, item_data, cmd_list, context)

    def write_mod(self, item_key, item_data_from, item_data, cmd_list, context):
        self.write_del(item_key, item_data_from, cmd_list, context)
        self.write_add(item_key, item_data, cmd_list, context)
        super().write_mod(item_key, item_data_from, item_data, cmd_list, context)

    def write_dict(self, item_key, item_node, cmd_list, context):
        raise NotImplementedError("write_dict not implemented for UniqueConstraintCmdGen")

CmdGen.register_cmd_gen('unique', 'unique', UniqueConstraintCmdGen)


class ForeignConstraintCmdGen(CmdGen):
    def write_add(self, item_key, item_data, cmd_list, context):
        key_name = f'fk_{item_key}'
        [foreign_table, foreign_col] = item_data.split('.')
        cmd_str = (
            f"ALTER TABLE {context['schema']}.{context['table']}"
            f" ADD CONSTRAINT {key_name}"
            f" FOREIGN KEY ({item_key})"
            f" REFERENCES {context['schema']}.{foreign_table} ({foreign_col})"
        )
        cmd_list.append(cmd_str)
        super().write_add(item_key, item_data, cmd_list, context)

    def write_del(self, item_key, item_data, cmd_list, context):
        key_name = f'fk_{item_key}'
        cmd_str = (
            f"ALTER TABLE {context['schema']}.{context['table']}"
            f" DROP CONSTRAINT IF EXISTS {key_name}"
        )
        cmd_list.append(cmd_str)
        super().write_del(item_key, item_data, cmd_list, context)

    def write_mod(self, item_key, item_data_from, item_data, cmd_list, context):
        self.write_del(item_key, item_data_from, cmd_list, context)
        self.write_add(item_key, item_data, cmd_list, context)
        super().write_mod(item_key, item_data_from, item_data, cmd_list, context)

    def write_dict(self, item_key, item_node, cmd_list, context):
        raise NotImplementedError("write_dict not implemented for ForeignConstraintCmdGen")

CmdGen.register_cmd_gen('foreign', 'foreign', ForeignConstraintCmdGen)