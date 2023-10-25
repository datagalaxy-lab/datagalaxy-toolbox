from typing import Optional

from toolbox.api.datagalaxy_api import get_access_token, Token
from toolbox.api.datagalaxy_api_dataprocessings import DataGalaxyApiDataprocessings
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace, DataGalaxyBulkResult


def copy_dataprocessings(url_source: str,
                         url_target: Optional[str],
                         token_source: str,
                         token_target: Optional[str],
                         workspace_source_name: str,
                         workspace_target_name: str) -> DataGalaxyBulkResult:
    if token_target is None:
        token_target = token_source

    if url_target is None:
        url_target = url_source

    integration_token_source = Token(token_source)
    integration_token_target = Token(token_target)
    source_access_token = get_access_token(url_source, integration_token_source)
    target_access_token = get_access_token(url_target, integration_token_target)

    workspaces_api_on_source_env = DataGalaxyApiWorkspace(
        url=url_source,
        access_token=source_access_token)
    source_workspace = workspaces_api_on_source_env.get_workspace(workspace_source_name)
    if source_workspace is None:
        raise Exception(f'workspace {workspace_source_name} does not exist')

    workspaces_api_on_target_env = DataGalaxyApiWorkspace(
        url=url_target,
        access_token=target_access_token
    )
    target_workspace = workspaces_api_on_target_env.get_workspace(workspace_target_name)
    if target_workspace is None:
        raise Exception(f'workspace {workspace_target_name} does not exist')

    dataprocessings_on_source_workspace = DataGalaxyApiDataprocessings(
        url=url_source,
        access_token=source_access_token,
        workspace=source_workspace
    )
    dataprocessings_on_target_workspace = DataGalaxyApiDataprocessings(
        url=url_target,
        access_token=target_access_token,
        workspace=target_workspace
    )

    # fetching dataprocessings from source workspace
    workspace_source_dataprocessings = dataprocessings_on_source_workspace.list_dataprocessings(workspace_source_name)

    for dp in workspace_source_dataprocessings:
        dp_index = workspace_source_dataprocessings.index(dp)
        items = dataprocessings_on_source_workspace.list_dataprocessing_items(workspace_name=workspace_source_name, parent_id=dp['id'])
        for item in items:
            item_index = items.index(item)
            del items[item_index]['summary']
            # for inputs and outputs, property 'path' must be named 'entityPath'
            for input in item['inputs']:
                input_index = item['inputs'].index(input)
                items[item_index]['inputs'][input_index]['entityPath'] = input['path']
            for output in item['outputs']:
                output_index = item['outputs'].index(output)
                items[item_index]['outputs'][output_index]['entityPath'] = output['path']
        workspace_source_dataprocessings[dp_index]['dataProcessingItems'] = items

    # copying the dataprocessings on the target workspace
    return dataprocessings_on_target_workspace.bulk_upsert_dataprocessings_tree(
        workspace_name=workspace_target_name,
        dataprocessings=workspace_source_dataprocessings
    )


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
        help='integration token source environnement',
        required=True)
    copy_dataprocessings_parse.add_argument(
        '--url-target',
        type=str,
        help='url target environnement (if undefined, use url source)')
    copy_dataprocessings_parse.add_argument(
        '--token-target',
        type=str,
        help='integration token target environnement (if undefined, use token source)')
    copy_dataprocessings_parse.add_argument(
        '--workspace-source',
        type=str,
        help='workspace source name',
        required=True)
    copy_dataprocessings_parse.add_argument(
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True)
