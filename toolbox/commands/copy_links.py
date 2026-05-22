import logging
from typing import Optional

from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.http_client import HttpClient
from toolbox.commands.utils import config_workspace, create_batches_of_links


def copy_links(url_source: str,
               url_target: Optional[str],
               token_source: str,
               token_target: Optional[str],
               workspace_source_name: str,
               version_source_name: Optional[str],
               workspace_target_name: str,
               version_target_name: Optional[str],
               http_client: HttpClient) -> int:
    if token_target is None:
        token_target = token_source

    if url_target is None:
        url_target = url_source

    # Source workspace
    source_workspace = config_workspace(
        mode="source",
        url=url_source,
        token=token_source,
        workspace_name=workspace_source_name,
        version_name=version_source_name,
        http_client=http_client
    )
    if not source_workspace:
        return 1

    # Target workspace
    target_workspace = config_workspace(
        mode="target",
        url=url_target,
        token=token_target,
        workspace_name=workspace_target_name,
        version_name=version_target_name,
        http_client=http_client
    )
    if not target_workspace:
        return 1

    # Fetch all objects from source workspace
    source_glossary_api = DataGalaxyApiModules(
        url=url_source,
        token=token_source,
        workspace=source_workspace,
        module="Glossary",
        http_client=http_client
    )
    source_dictionary_api = DataGalaxyApiModules(
        url=url_source,
        token=token_source,
        workspace=source_workspace,
        module="Dictionary",
        http_client=http_client
    )
    source_dataprocessings_api = DataGalaxyApiModules(
        url=url_source,
        token=token_source,
        workspace=source_workspace,
        module="DataProcessing",
        http_client=http_client
    )
    source_usages_api = DataGalaxyApiModules(
        url=url_source,
        token=token_source,
        workspace=source_workspace,
        module="Uses",
        http_client=http_client
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
        module="Links",
        http_client=http_client
    )

    # Creating links in target workspace, one call per batch
    for batch in link_batches:
        target_links_api.bulk_upsert_tree(workspace_name=workspace_target_name, bulktree=batch)
    return 0


# This is a WIP and not used yet in the codebase
def handle_reference_data_value(source_glossary: list) -> str:
    for page in source_glossary:
        page_index = source_glossary.index(page)
        for glossary_object in page:
            go_index = page.index(glossary_object)
            if glossary_object['type'] == 'ReferenceDataValue' and glossary_object['links']:
                if 'attributes' in glossary_object and 'code' in glossary_object['attributes']:
                    new_path = glossary_object['path'] + '\\' + glossary_object['attributes']['code']
                    new_type_path = glossary_object['typePath'].replace('\\ReferenceDataValue', '\\Value\\ValueCode')
                    page[go_index]['path'] = new_path
                    page[go_index]['typePath'] = new_type_path
                else:
                    logging.warning(f'Links of Reference Data Value {glossary_object["technicalName"]} cannot be imported without editor attribute Code')
                    logging.warning('Please add it to your DataGalaxy screen for Reference Data Value objects')
        source_glossary[page_index] = page


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
        '--version-source',
        type=str,
        help='version source name')
    copy_links_parse.add_argument(
        '--workspace-target',
        type=str,
        help='workspace target name',
        required=True)
    copy_links_parse.add_argument(
        '--version-target',
        type=str,
        help='version target name')
