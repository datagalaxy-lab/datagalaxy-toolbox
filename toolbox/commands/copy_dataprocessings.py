from typing import Optional

from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace


def copy_dataprocessings(url_source: str,
                         url_target: Optional[str],
                         token_source: str,
                         token_target: Optional[str],
                         workspace_source_name: str,
                         workspace_target_name: str,
                         tag_value: Optional[str]) -> int:
    if token_target is None:
        token_target = token_source

    if url_target is None:
        url_target = url_source

    workspaces_api_on_source_env = DataGalaxyApiWorkspace(
        url=url_source,
        token=token_source)
    source_workspace = workspaces_api_on_source_env.get_workspace(workspace_source_name)
    if source_workspace is None:
        raise Exception(f'workspace {workspace_source_name} does not exist')

    workspaces_api_on_target_env = DataGalaxyApiWorkspace(
        url=url_target,
        token=token_target
    )
    target_workspace = workspaces_api_on_target_env.get_workspace(workspace_target_name)
    if target_workspace is None:
        raise Exception(f'workspace {workspace_target_name} does not exist')

    source_module_api = DataGalaxyApiModules(
        url=url_source,
        token=token_source,
        workspace=workspaces_api_on_source_env.get_workspace(workspace_source_name),
        module="DataProcessing"
    )
    target_module_api = DataGalaxyApiModules(
        url=url_target,
        token=token_target,
        workspace=workspaces_api_on_target_env.get_workspace(workspace_target_name),
        module="DataProcessing"
    )

    # fetch objects from source workspace
    source_objects = source_module_api.list_objects(workspace_source_name)

    # fetch dataprocessingsitems for each dp in source workspace (but not dataflows)
    for page in source_objects:
        page_index = source_objects.index(page)
        for dp in page:
            if dp['type'] == "DataFlow":
                # a DataFlow do not have dpi
                continue
            dp_index = page.index(dp)
            items = source_module_api.list_object_items(workspace_name=workspace_source_name, parent_id=dp['id'])
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
        source_objects[page_index] = page

    # create objects on target workspace
    target_module_api.bulk_upsert_tree(
        workspace_name=workspace_target_name,
        objects=source_objects,
        tag_value=tag_value
    )

    return 0


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
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True),
    copy_dataprocessings_parse.add_argument(
        '--tag-value',
        type=str,
        help='select tag value to filter objects')
