from typing import Optional

from toolbox.api.datagalaxy_api import DataGalaxyBulkResult
from toolbox.api.datagalaxy_api_glossary import DataGalaxyApiGlossary
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace


def copy_glossary(url_source: str,
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

    workspaces_api_on_source_env = DataGalaxyApiWorkspace(
        url=url_source,
        token=token_source)

    workspaces_api_on_target_env = DataGalaxyApiWorkspace(
        url=url_target,
        token=token_target
    )

    workspace_source = workspaces_api_on_source_env.get_workspace(workspace_source_name)
    workspace_target = workspaces_api_on_target_env.get_workspace(workspace_target_name)

    if workspace_target:
        # on récupère les propriétés du glossary du workspace_source
        glossary_on_source_workspace = DataGalaxyApiGlossary(
            url=url_source,
            token=token_source,
            workspace=workspace_source
        )
        workspace_source_glossary_properties = glossary_on_source_workspace.list_properties(
            workspace_source_name)

        # on copie ces propriétés sur le workspace_target
        glossary_on_target_workspace = DataGalaxyApiGlossary(
            url=url_target,
            token=token_target,
            workspace=workspace_target
        )
        return glossary_on_target_workspace.bulk_upsert_property_tree(
            workspace_name=workspace_target_name,
            properties=workspace_source_glossary_properties,
            tag_value=tag_value
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
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True)
    copy_glossary_parse.add_argument(
        '--tag-value',
        type=str,
        help='select tag value to filter objects')
