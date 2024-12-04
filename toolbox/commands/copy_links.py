import logging
from typing import Optional

from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace


def copy_links(url_source: str,
               url_target: Optional[str],
               token_source: str,
               token_target: Optional[str],
               workspace_source_name: str,
               workspace_target_name: str) -> int:
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

    source_glossary_api = DataGalaxyApiModules(
        url=url_source,
        token=token_source,
        workspace=workspaces_api_on_source_env.get_workspace(workspace_source_name),
        module="Glossary"
    )
    source_dictionary_api = DataGalaxyApiModules(
        url=url_source,
        token=token_source,
        workspace=workspaces_api_on_source_env.get_workspace(workspace_source_name),
        module="Dictionary"
    )
    source_dataprocessings_api = DataGalaxyApiModules(
        url=url_source,
        token=token_source,
        workspace=workspaces_api_on_source_env.get_workspace(workspace_source_name),
        module="DataProcessing"
    )
    source_usages_api = DataGalaxyApiModules(
        url=url_source,
        token=token_source,
        workspace=workspaces_api_on_source_env.get_workspace(workspace_source_name),
        module="Uses"
    )

    # Find all links in source workspace
    source_glossary = source_glossary_api.list_objects(workspace_source_name, include_links=True)
    source_dataprocessings = source_dataprocessings_api.list_objects(workspace_source_name, include_links=True)
    source_usages = source_usages_api.list_objects(workspace_source_name, include_links=True)
    source_dictionary = source_dictionary_api.list_objects(workspace_source_name, include_links=True)
    source_dictionary_children = []
    for page in source_dictionary:
        for source in page:
            source_id = source['id']
            containers = source_dictionary_api.list_children_objects(workspace_source_name, source_id, "containers", include_links=True)
            structures = source_dictionary_api.list_children_objects(workspace_source_name, source_id, "structures", include_links=True)
            fields = source_dictionary_api.list_children_objects(workspace_source_name, source_id, "fields", include_links=True)
            source_dictionary_children += containers
            source_dictionary_children += structures
            source_dictionary_children += fields
    # Collecting all links
    link_batches = create_batches_of_links(source_glossary + source_dictionary + source_dataprocessings + source_usages + source_dictionary_children)
    count_links = 0
    for batch in link_batches:
        count_links += len(batch)
    logging.info(f'copy-links - {count_links} links found')

    target_links_api = DataGalaxyApiModules(
        url=url_target,
        token=token_target,
        workspace=target_workspace,
        module="Links"
    )

    # # Creating links in target workspace
    target_links_api.bulk_create_links(workspace_name=workspace_target_name, links=link_batches)
    return 0


def create_batches_of_links(input_arrays, max_size=5000):
    batches = []  # This will hold the list of arrays
    current_batch = []  # Temporary array to build chunks

    for arr in input_arrays:
        for obj in arr:  # Add each object from the input array
            links = parse_links(obj)
            if len(current_batch) < max_size:
                current_batch += links
            else:
                # When the current array reaches max size, save it and start a new one
                batches.append(current_batch)
                current_batch = links

    # Add the remaining objects in `current_batch` if it's not empty
    if current_batch:
        batches.append(current_batch)

    return batches


def parse_links(obj: dict) -> list:
    links = []
    # DPI are ignored since they are handled differently
    if "DataProcessingItem" in obj["typePath"]:
        return []
    for key in obj["links"]:
        for dest in obj["links"][key]:
            if "DataProcessingItem" in dest["typePath"]:
                continue
            link = {
                    'fromPath': obj["path"],
                    'fromType': obj["typePath"],
                    'linkType': key,
                    'toPath': dest["path"],
                    'toType': dest["typePath"]
                    }
            links.append(link)
    return links


def copy_links_parse(subparsers):
    # create the parser for the "copy_links" command
    copy_links_parse = subparsers.add_parser('copy-links', help='copy-links help')
    copy_links_parse.add_argument(
        '--url-source',
        type=str,
        help='url source environnement',
        required=True)
    copy_links_parse.add_argument(
        '--token-source',
        type=str,
        help='token source environnement',
        required=True)
    copy_links_parse.add_argument(
        '--url-target',
        type=str,
        help='url target environnement (if undefined, use url source)')
    copy_links_parse.add_argument(
        '--token-target',
        type=str,
        help='token target environnement (if undefined, use token source)')
    copy_links_parse.add_argument(
        '--workspace-source',
        type=str,
        help='workspace source name',
        required=True)
    copy_links_parse.add_argument(
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True)
