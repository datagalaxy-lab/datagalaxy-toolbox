import logging
from typing import Optional

from toolbox.api.datagalaxy_api import get_access_token, Token
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace, DataGalaxyApiGlossary, \
    DataGalaxyBulkResult


def copy_glossary(url_source: str,
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

    workspace_source = workspaces_api_on_source_env.get_workspace(workspace_source_name)
    workspace_target = workspaces_api_on_target_env.get_workspace(workspace_target_name)

    if workspace_target:
        # on récupère les propriétés du glossary du workspace_source
        glossary_on_source_workspace = DataGalaxyApiGlossary(
            url=url_source,
            access_token=source_access_token,
            workspace=workspace_source
        )
        workspace_source_glossary_properties = glossary_on_source_workspace.list_glossary_properties(
            workspace_source_name)
        logging.info(f'glossary properties on source workspace : {workspace_source_glossary_properties}')
        # on copie ces propriétés sur le workspace_target
        glossary_on_target_workspace = DataGalaxyApiGlossary(
            url=url_target,
            access_token=target_access_token,
            workspace=workspace_target
        )
        return glossary_on_target_workspace.bulk_upsert_property_tree(
            workspace_name=workspace_target_name,
            properties=workspace_source_glossary_properties
        )

    raise Exception(f'workspace {workspace_target_name} does not exist')


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
        help='integration token source environnement',
        required=True)
    copy_glossary_parse.add_argument(
        '--url-target',
        type=str,
        help='url target environnement (if undefined, use url source)')
    copy_glossary_parse.add_argument(
        '--token-target',
        type=str,
        help='integration token target environnement (if undefined, use token source)')
    copy_glossary_parse.add_argument(
        '--workspace-source',
        type=str,
        help='workspace source name',
        required=True)
    copy_glossary_parse.add_argument(
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True)
