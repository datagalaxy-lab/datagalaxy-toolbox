import logging
from typing import Optional

from toolbox.api.datagalaxy_api import get_access_token, Token
from toolbox.api.datagalaxy_api_usages import DataGalaxyApiUsages
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace, DataGalaxyBulkResult


def copy_usages(url_source: str,
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

    workspaces_api_on_target_env = DataGalaxyApiWorkspace(
        url=url_target,
        access_token=target_access_token
    )
    usages_on_source_workspace = DataGalaxyApiUsages(
        url=url_source,
        access_token=source_access_token,
        workspace=workspaces_api_on_source_env.get_workspace(workspace_source_name)
    )
    usages_on_target_workspace = DataGalaxyApiUsages(
        url=url_target,
        access_token=target_access_token,
        workspace=workspaces_api_on_target_env.get_workspace(workspace_target_name)
    )

    if workspaces_api_on_target_env.get_workspace(workspace_target_name):
        # on récupère les usages du workspace_source
        workspace_source_usages = usages_on_source_workspace.list_usages(workspace_source_name)
        logging.info(f'Usages on source workspace : {workspace_source_usages}')

        # on copie ces usages sur le workspace_target
        return usages_on_target_workspace.bulk_upsert_usages_tree(
            workspace_name=workspace_target_name,
            usages=workspace_source_usages
        )

    raise Exception(f'workspace {workspace_target_name} does not exist')


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
        help='integration token source environnement',
        required=True)
    copy_usages_parse.add_argument(
        '--url-target',
        type=str,
        help='url target environnement (if undefined, use url source)')
    copy_usages_parse.add_argument(
        '--token-target',
        type=str,
        help='integration token target environnement (if undefined, use token source)')
    copy_usages_parse.add_argument(
        '--workspace-source',
        type=str,
        help='workspace source name',
        required=True)
    copy_usages_parse.add_argument(
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True)
