from typing import Optional

from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace


def copy_glossary(url_source: str,
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
        module="Glossary"
    )
    target_module_api = DataGalaxyApiModules(
        url=url_target,
        token=token_target,
        workspace=workspaces_api_on_target_env.get_workspace(workspace_target_name),
        module="Glossary"
    )

    # fetch objects from source workspace
    source_objects = source_module_api.list_objects(workspace_source_name)

    # create objects on target workspace
    target_module_api.bulk_upsert_tree(
        workspace_name=workspace_target_name,
        objects=source_objects,
        tag_value=tag_value
    )

    return 0


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
