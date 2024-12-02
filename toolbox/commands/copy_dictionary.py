from typing import Optional

from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace


def copy_dictionary(url_source: str,
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
        token=token_source
    )
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

    source_dictionary_api = DataGalaxyApiModules(
        url=url_source,
        token=token_source,
        workspace=workspaces_api_on_source_env.get_workspace(workspace_source_name),
        module="Dictionary"
    )
    target_dictionary_api = DataGalaxyApiModules(
        url=url_target,
        token=token_target,
        workspace=target_workspace,
        module="Dictionary"
    )

    # fetch sources (databases) from source workspace
    source_sources = source_dictionary_api.list_objects(workspace_source_name)

    for page in source_sources:
        for source in page:
            # fetch children objects for each source
            source_id = source['id']
            containers = source_dictionary_api.list_children_objects(workspace_source_name, source_id, "containers")
            structures = source_dictionary_api.list_children_objects(workspace_source_name, source_id, "structures")
            fields = source_dictionary_api.list_children_objects(workspace_source_name, source_id, "fields")
            # todo : fetch primary keys and foreign keys

            # bulk upsert source tree
            target_dictionary_api.bulk_upsert_source_tree(
                workspace_name=workspace_target_name,
                source=source,
                objects=containers + structures + fields,
                tag_value=tag_value
            )

    return 0


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
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True),
    copy_dictionary_parse.add_argument(
        '--tag-value',
        type=str,
        help='select tag value to filter objects')
