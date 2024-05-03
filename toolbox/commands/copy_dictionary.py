from typing import Optional

from toolbox.api.datagalaxy_api import get_access_token, Token, DataGalaxyBulkResult
from toolbox.api.datagalaxy_api_dictionary import DataGalaxyApiDictionary
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace


def copy_dictionary(url_source: str,
                    url_target: Optional[str],
                    token_source: str,
                    token_target: Optional[str],
                    workspace_source_name: str,
                    workspace_target_name: str,
                    tag_value: Optional[str]) -> DataGalaxyBulkResult:
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
        access_token=source_access_token
    )
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

    dictionary_on_source_workspace = DataGalaxyApiDictionary(
        url=url_source,
        access_token=source_access_token,
        workspace=workspaces_api_on_source_env.get_workspace(workspace_source_name)
    )
    dictionary_on_target_workspace = DataGalaxyApiDictionary(
        url=url_target,
        access_token=target_access_token,
        workspace=target_workspace
    )

    # fetching sources from workspace_source
    source_sources = dictionary_on_source_workspace.list_sources(workspace_source_name)
    source_all = source_sources

    # fetching containers from workspace_source
    source_containers = dictionary_on_source_workspace.list_containers(workspace_source_name)
    source_all = source_all + source_containers

    # fetching structures from workspace_source
    source_structures = dictionary_on_source_workspace.list_structures(workspace_source_name)
    source_all = source_all + source_structures

    # fetching fields from workspace_source
    source_fields = dictionary_on_source_workspace.list_fields(workspace_source_name)
    source_all = source_all + source_fields

    # copy all the dictionary in workspace_target
    return dictionary_on_target_workspace.bulk_upsert_sources_tree(
        workspace_name=workspace_target_name,
        sources=source_all,
        tag_value=tag_value
    )


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
        help='integration token source environnement',
        required=True)
    copy_dictionary_parse.add_argument(
        '--url-target',
        type=str,
        help='url target environnement (if undefined, use url source)')
    copy_dictionary_parse.add_argument(
        '--token-target',
        type=str,
        help='integration token target environnement (if undefined, use token source)')
    copy_dictionary_parse.add_argument(
        '--workspace-source',
        type=str,
        help='workspace source name',
        required=True)
    copy_dictionary_parse.add_argument(
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True),
    copy_dictionary_parse.add_argument(
        '--tag-value',
        type=str,
        help='select tag value to filter objects')
