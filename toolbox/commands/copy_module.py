from typing import Optional
import logging

from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.commands.utils import config_workspace


def copy_module(module: str,
                url_source: str,
                url_target: Optional[str],
                token_source: str,
                token_target: Optional[str],
                workspace_source_name: str,
                version_source_name: Optional[str],
                workspace_target_name: str,
                version_target_name: Optional[str],
                tag_value: Optional[str]) -> int:
    # Tokens
    if token_target is None:
        token_target = token_source

    # URL
    if url_target is None:
        url_target = url_source

    # Source workspace
    source_workspace = config_workspace(
        mode="source",
        url=url_source,
        token=token_source,
        workspace_name=workspace_source_name,
        version_name=version_source_name
    )
    if not source_workspace:
        return 1

    # Target workspace
    target_workspace = config_workspace(
        mode="target",
        url=url_target,
        token=token_target,
        workspace_name=workspace_target_name,
        version_name=version_target_name
    )
    if not target_workspace:
        return 1

    # Source module
    source_module_api = DataGalaxyApiModules(
        url=url_source,
        token=token_source,
        workspace=source_workspace,
        module=module
    )

    # Target module
    target_module_api = DataGalaxyApiModules(
        url=url_target,
        token=token_target,
        workspace=target_workspace,
        module=module
    )

    # Fetch objects from source workspace
    source_objects = source_module_api.list_objects(workspace_source_name)
    if source_objects == [[]]:
        logging.warning(f'copy-module - No object in source workspace {workspace_source_name}, aborting.')
        return 1

    # Specific for Dictionary
    if module == "Dictionary":
        for page in source_objects:
            for source in page:
                # fetch children objects for each source
                source_id = source['id']
                source_path = source['path']
                # Children objects
                containers = source_module_api.list_children_objects(workspace_source_name, source_id, "containers")
                structures = source_module_api.list_children_objects(workspace_source_name, source_id, "structures")
                fields = source_module_api.list_children_objects(workspace_source_name, source_id, "fields")

                primary_keys = source_module_api.list_keys(workspace_source_name, source_id, "primary")
                foreign_keys = source_module_api.list_keys(workspace_source_name, source_id, "foreign")
                pks = []
                fks = []
                # PK
                for primary_key in primary_keys:
                    pk_name = primary_key['technicalName']
                    table_id = primary_key["table"]["id"]
                    table_path = ""
                    for page in structures:
                        for table in page:
                            if table["id"] == table_id:
                                table_path = table["path"]
                    for column in primary_key["columns"]:
                        column_name = column["technicalName"]
                        pk_order = column["pkOrder"]
                        pk = {
                            'tablePath': table_path.replace(source_path, "", 1),
                            'columnName': column_name,
                            'pkName': pk_name,
                            'pkOrder': pk_order
                        }
                        pks.append(pk)
                # FK
                for foreign_key in foreign_keys:
                    fk_technical_name = foreign_key['technicalName']
                    fk_display_name = foreign_key['displayName']
                    if len(foreign_key['columns']) < 1:
                        logging.warn(f"FK {fk_technical_name} is a functional relationship, ignoring")
                        continue
                    pk_technical_name = foreign_key['primaryKey']['technicalName']
                    pk_table_id = foreign_key['parents']['structure']['id']
                    pk_table_path = ""
                    for page in structures:
                        for table in page:
                            if table["id"] == pk_table_id:
                                pk_table_path = table["path"]
                    fk_table_id = foreign_key['children']['structure']['id']
                    fk_table_path = ""
                    for page in structures:
                        for table in page:
                            if table["id"] == fk_table_id:
                                fk_table_path = table["path"]
                    parent_columns = foreign_key['parents']['columns']
                    if len(parent_columns) > 1:
                        # print("More than 1 column")
                        continue
                    for parent_column in parent_columns:
                        pk_column_name = parent_column['technicalName']

                    children_columns = foreign_key['children']['columns']
                    if len(children_columns) > 1:
                        # print("More than 1 column, ignoring this one")
                        continue
                    for children_column in children_columns:
                        fk_column_name = children_column['technicalName']
                    fk = {
                        'fkTechnicalName': fk_technical_name,
                        'pkTechnicalName': pk_technical_name,
                        'pkTablePath': pk_table_path.replace(source_path, "", 1),
                        'pkColumnName': pk_column_name,
                        'fkTablePath': fk_table_path.replace(source_path, "", 1),
                        'fkColumnName': fk_column_name,
                        'fkDisplayName': fk_display_name
                    }
                    fks.append(fk)

                # create new source to fetch its id
                new_source_id = target_module_api.create_source(
                    workspace_name=workspace_target_name,
                    source=source
                )

                # bulk upsert source tree
                target_module_api.bulk_upsert_source_tree(
                    workspace_name=workspace_target_name,
                    source=source,
                    objects=containers + structures + fields,
                    tag_value=tag_value
                )

                # create PKs and FKs if they exist
                if len(pks) > 0:
                    target_module_api.create_keys(
                        workspace_name=workspace_target_name,
                        source_id=new_source_id,
                        keys=pks,
                        mode="primary")
                if len(fks) > 0:
                    target_module_api.create_keys(
                        workspace_name=workspace_target_name,
                        source_id=new_source_id,
                        keys=fks,
                        mode="foreign")
    else:
        # Specific for DPs
        if module == "DataProcessing":
            handle_dpis(source_objects, source_module_api, workspace_source_name)

        # Create objects on target workspace
        target_module_api.bulk_upsert_tree(
            workspace_name=workspace_target_name,
            objects=source_objects,
            tag_value=tag_value
        )

    return 0


# This is specific for the DataProcessings module
def handle_dpis(objects: list, module_api, workspace_name: str):
    # fetch dataprocessingsitems for each dp in source workspace (but not dataflows)
    for page in objects:
        page_index = objects.index(page)
        for dp in page:
            if dp['type'] == "DataFlow":
                # a DataFlow do not have dpi
                continue
            dp_index = page.index(dp)
            items = module_api.list_object_items(workspace_name=workspace_name, parent_id=dp['id'])
            if len(items) < 1:
                # no dpi, let's move on to the next one
                continue
            for item in items:
                item_index = items.index(item)
                # some objects have no summary, and some have a summary but set to "None" which raises an error in the API somehow
                if "summary" in items[item_index] and items[item_index]['summary'] is None:
                    items[item_index]['summary'] = ""
                # for inputs and outputs, property 'path' must be named 'entityPath'
                if 'inputs' in item:
                    for input in item['inputs']:
                        input_index = item['inputs'].index(input)
                        items[item_index]['inputs'][input_index]['entityPath'] = input['path']
                else:
                    items[item_index]['inputs'] = []
                if 'outputs' in item:
                    for output in item['outputs']:
                        output_index = item['outputs'].index(output)
                        items[item_index]['outputs'][output_index]['entityPath'] = output['path']
                else:
                    items[item_index]['outputs'] = []
                # there is a problem with dpi types, we must map them to the correct value (accepted by the API)
                if item['type'] == "Search":
                    items[item_index]['type'] = "Lookup"
                if item['type'] == "ConstantVariable":
                    items[item_index]['type'] = "Variable"
                if item['type'] == "Calculation":
                    items[item_index]['type'] = "AnalyticalCalculation"
            page[dp_index]['dataProcessingItems'] = items
        objects[page_index] = page


# Parsers
def copy_glossary_parse(subparsers):
    # create the parser for the "copy_glossary" command
    copy_glossary_parse = subparsers.add_parser('copy-glossary', help='copy-glossary help')
    copy_glossary_parse.add_argument(
        '--url-source',
        type=str,
        help='url source environnement',
        required=True)
    copy_glossary_parse.add_argument(
        '--token-source',
        type=str,
        help='token source environnement',
        required=True)
    copy_glossary_parse.add_argument(
        '--url-target',
        type=str,
        help='url target environnement (if undefined, use url source)')
    copy_glossary_parse.add_argument(
        '--token-target',
        type=str,
        help='token target environnement (if undefined, use token source)')
    copy_glossary_parse.add_argument(
        '--workspace-source',
        type=str,
        help='workspace source name',
        required=True)
    copy_glossary_parse.add_argument(
        '--version-source',
        type=str,
        help='version source name')
    copy_glossary_parse.add_argument(
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True)
    copy_glossary_parse.add_argument(
        '--version-target',
        type=str,
        help='version target name')
    copy_glossary_parse.add_argument(
        '--tag-value',
        type=str,
        help='select tag value to filter objects')


def copy_dictionary_parse(subparsers):
    # create the parser for the "copy_dictionary" command
    copy_dictionary_parse = subparsers.add_parser('copy-dictionary', help='copy-dictionary help')
    copy_dictionary_parse.add_argument(
        '--url-source',
        type=str,
        help='url source environnement',
        required=True)
    copy_dictionary_parse.add_argument(
        '--token-source',
        type=str,
        help='token source environnement',
        required=True)
    copy_dictionary_parse.add_argument(
        '--url-target',
        type=str,
        help='url target environnement (if undefined, use url source)')
    copy_dictionary_parse.add_argument(
        '--token-target',
        type=str,
        help='token target environnement (if undefined, use token source)')
    copy_dictionary_parse.add_argument(
        '--workspace-source',
        type=str,
        help='workspace source name',
        required=True)
    copy_dictionary_parse.add_argument(
        '--version-source',
        type=str,
        help='version source name')
    copy_dictionary_parse.add_argument(
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True)
    copy_dictionary_parse.add_argument(
        '--version-target',
        type=str,
        help='version target name')
    copy_dictionary_parse.add_argument(
        '--tag-value',
        type=str,
        help='select tag value to filter objects')


def copy_dataprocessings_parse(subparsers):
    # create the parser for the "copy_dataprocessings" command
    copy_dataprocessings_parse = subparsers.add_parser('copy-dataprocessings', help='copy-dataprocessings help')
    copy_dataprocessings_parse.add_argument(
        '--url-source',
        type=str,
        help='url source environnement',
        required=True)
    copy_dataprocessings_parse.add_argument(
        '--token-source',
        type=str,
        help='token source environnement',
        required=True)
    copy_dataprocessings_parse.add_argument(
        '--url-target',
        type=str,
        help='url target environnement (if undefined, use url source)')
    copy_dataprocessings_parse.add_argument(
        '--token-target',
        type=str,
        help='token target environnement (if undefined, use token source)')
    copy_dataprocessings_parse.add_argument(
        '--workspace-source',
        type=str,
        help='workspace source name',
        required=True)
    copy_dataprocessings_parse.add_argument(
        '--version-source',
        type=str,
        help='version source name')
    copy_dataprocessings_parse.add_argument(
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True),
    copy_dataprocessings_parse.add_argument(
        '--version-target',
        type=str,
        help='version target name')
    copy_dataprocessings_parse.add_argument(
        '--tag-value',
        type=str,
        help='select tag value to filter objects')


def copy_usages_parse(subparsers):
    # create the parser for the "copy_usages" command
    copy_usages_parse = subparsers.add_parser('copy-usages', help='copy-usages help')
    copy_usages_parse.add_argument(
        '--url-source',
        type=str,
        help='url source environnement',
        required=True)
    copy_usages_parse.add_argument(
        '--token-source',
        type=str,
        help='token source environnement',
        required=True)
    copy_usages_parse.add_argument(
        '--url-target',
        type=str,
        help='url target environnement (if undefined, use url source)')
    copy_usages_parse.add_argument(
        '--token-target',
        type=str,
        help='token target environnement (if undefined, use token source)')
    copy_usages_parse.add_argument(
        '--workspace-source',
        type=str,
        help='workspace source name',
        required=True)
    copy_usages_parse.add_argument(
        '--version-source',
        type=str,
        help='version source name')
    copy_usages_parse.add_argument(
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True)
    copy_usages_parse.add_argument(
        '--version-target',
        type=str,
        help='version target name')
    copy_usages_parse.add_argument(
        '--tag-value',
        type=str,
        help='select tag value to filter objects')
