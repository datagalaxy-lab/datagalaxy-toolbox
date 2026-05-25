from typing import Optional
import logging
from datetime import datetime
from pathlib import Path

from toolbox.api.datagalaxy_api import build_bulktree, create_batches
from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.http_client import HttpClient
from toolbox.commands.utils import config_workspace, flatten_pages, write_file


def export_module(module: str,
                  url: str,
                  token: str,
                  workspace_name: str,
                  version_name: Optional[str],
                  http_client: HttpClient,
                  bulktree: bool = False) -> int:
    # Source workspace
    workspace = config_workspace(
        mode="source",
        url=url,
        token=token,
        workspace_name=workspace_name,
        version_name=version_name,
        http_client=http_client
    )
    if not workspace:
        return 1

    # Source module API
    module_api = DataGalaxyApiModules(
        url=url,
        token=token,
        workspace=workspace,
        module=module,
        http_client=http_client
    )

    # Fetch objects from source workspace
    objects = module_api.list_objects(workspace_name)
    if objects == [[]]:
        logging.warning(f'export-module - No object in workspace {workspace_name}, aborting.')
        return 1

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_dir = Path("export")
    export_dir.mkdir(parents=True, exist_ok=True)

    # Specific for Dictionary
    if module == "Dictionary":
        for page in objects:
            # Sources
            if not bulktree:
                filename = f"{workspace_name}_{module}_0_sources_{timestamp}.json"
                write_file(filename, export_dir, page)
            for source in page:
                # fetch children objects for each source
                id = source['id']
                path = source['path']
                source_name = source['name']
                # Children objects
                containers = module_api.list_children_objects(workspace_name, id, "containers")
                structures = module_api.list_children_objects(workspace_name, id, "structures")
                fields = module_api.list_children_objects(workspace_name, id, "fields")

                primary_keys = module_api.list_keys(workspace_name, id, "primary")
                foreign_keys = module_api.list_keys(workspace_name, id, "foreign")
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
                            'tablePath': table_path.replace(path, "", 1),
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
                        continue
                    for parent_column in parent_columns:
                        pk_column_name = parent_column['technicalName']

                    children_columns = foreign_key['children']['columns']
                    if len(children_columns) > 1:
                        continue
                    for children_column in children_columns:
                        fk_column_name = children_column['technicalName']
                    fk = {
                        'fkTechnicalName': fk_technical_name,
                        'pkTechnicalName': pk_technical_name,
                        'pkTablePath': pk_table_path.replace(path, "", 1),
                        'pkColumnName': pk_column_name,
                        'fkTablePath': fk_table_path.replace(path, "", 1),
                        'fkColumnName': fk_column_name,
                        'fkDisplayName': fk_display_name
                    }
                    fks.append(fk)

                if bulktree:
                    # Build bulktree for each batch and dump all of them in one
                    bulktrees = []
                    # Create batches
                    batches = create_batches(containers + structures + fields)
                    # One bulktree call per batch
                    for batch in batches:
                        bulktree = build_bulktree([source] + batch)
                        if len(bulktree) > 1:
                            raise Exception(f"Problem while creating the bulktree for source {source['name']}")
                        bulktree = bulktree[0]
                        bulktrees.append(bulktree)
                    filename = f"{workspace_name}_{module}_{source_name}_bulktrees_{timestamp}.json"
                    write_file(filename, export_dir, bulktrees)

                else:
                    # Containers
                    filename = f"{workspace_name}_{module}_{source_name}_1_containers_{timestamp}.json"
                    write_file(filename, export_dir, flatten_pages(containers))
                    # Structures
                    filename = f"{workspace_name}_{module}_{source_name}_2_structures_{timestamp}.json"
                    write_file(filename, export_dir, flatten_pages(structures))

                    # Fields
                    filename = f"{workspace_name}_{module}_{source_name}_3_fields_{timestamp}.json"
                    write_file(filename, export_dir, flatten_pages(fields))

                # PKs
                filename = f"{workspace_name}_{module}_{source_name}_4_pks_{timestamp}.json"
                write_file(filename, export_dir, pks)

                # FKs
                filename = f"{workspace_name}_{module}_{source_name}_5_fks_{timestamp}.json"
                write_file(filename, export_dir, fks)

    else:
        # Specific for DPs
        if module == "DataProcessing":
            handle_dpis(objects, module_api, workspace_name)

        export_dir.mkdir(parents=True, exist_ok=True)
        if bulktree:
            # Build bulktree for each page and dump all of them in one
            bulktrees = []
            for page in objects:
                bulktree = build_bulktree(page)
                bulktrees.append(bulktree)
            filename = f"{workspace_name}_{module}_bulktrees_{timestamp}.json"
            write_file(filename, export_dir, bulktrees)
        else:
            # Dump all pages in one file
            filename = f"{workspace_name}_{module}_{timestamp}.json"
            write_file(filename, export_dir, flatten_pages(objects))

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
                # Mapping some DPI types
                if item['type'] == "Search":
                    items[item_index]['type'] = "Lookup"
                if item['type'] == "ConstantVariable":
                    # items[item_index]['type'] = "Variable" (temporary)
                    items[item_index]['type'] = "Undefined"
                if item['type'] == "Calculation":
                    # items[item_index]['type'] = "AnalyticalCalculation" (temporary)
                    items[item_index]['type'] = "Undefined"
            page[dp_index]['dataProcessingItems'] = items
        objects[page_index] = page


# Parsers
def export_glossary_parse(subparsers):
    # create the parser for the "export_glossary" command
    export_glossary_parse = subparsers.add_parser('export-glossary', help='export-glossary help')
    export_glossary_parse.add_argument(
        '--url',
        type=str,
        help='url source environnement',
        required=True)
    export_glossary_parse.add_argument(
        '--token',
        type=str,
        help='token source environnement',
        required=True)
    export_glossary_parse.add_argument(
        '--workspace',
        type=str,
        help='workspace source name',
        required=True)
    export_glossary_parse.add_argument(
        '--version',
        type=str,
        help='version source name')
    export_glossary_parse.add_argument(
        '--bulktree',
        action='store_true',
        help='export objects as a bulktree')


def export_dictionary_parse(subparsers):
    # create the parser for the "export_dictionary" command
    export_dictionary_parse = subparsers.add_parser('export-dictionary', help='export-dictionary help')
    export_dictionary_parse.add_argument(
        '--url',
        type=str,
        help='url source environnement',
        required=True)
    export_dictionary_parse.add_argument(
        '--token',
        type=str,
        help='token source environnement',
        required=True)
    export_dictionary_parse.add_argument(
        '--workspace',
        type=str,
        help='workspace source name',
        required=True)
    export_dictionary_parse.add_argument(
        '--version',
        type=str,
        help='version source name')
    export_dictionary_parse.add_argument(
        '--bulktree',
        action='store_true',
        help='export objects as a bulktree')


def export_dataprocessings_parse(subparsers):
    # create the parser for the "export_dataprocessings" command
    export_dataprocessings_parse = subparsers.add_parser('export-dataprocessings', help='export-dataprocessings help')
    export_dataprocessings_parse.add_argument(
        '--url',
        type=str,
        help='url source environnement',
        required=True)
    export_dataprocessings_parse.add_argument(
        '--token',
        type=str,
        help='token source environnement',
        required=True)
    export_dataprocessings_parse.add_argument(
        '--workspace',
        type=str,
        help='workspace source name',
        required=True)
    export_dataprocessings_parse.add_argument(
        '--version',
        type=str,
        help='version source name')
    export_dataprocessings_parse.add_argument(
        '--bulktree',
        action='store_true',
        help='export objects as a bulktree')


def export_usages_parse(subparsers):
    # create the parser for the "export_usages" command
    export_usages_parse = subparsers.add_parser('export-usages', help='export-usages help')
    export_usages_parse.add_argument(
        '--url',
        type=str,
        help='url source environnement',
        required=True)
    export_usages_parse.add_argument(
        '--token',
        type=str,
        help='token source environnement',
        required=True)
    export_usages_parse.add_argument(
        '--workspace',
        type=str,
        help='workspace source name',
        required=True)
    export_usages_parse.add_argument(
        '--version',
        type=str,
        help='version source name')
    export_usages_parse.add_argument(
        '--bulktree',
        action='store_true',
        help='export objects as a bulktree')
