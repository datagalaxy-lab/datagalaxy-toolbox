import logging
from typing import Optional

from toolbox.api.datagalaxy_api import DataGalaxyBulkResult
from toolbox.api.datagalaxy_api_usages import DataGalaxyApiUsages
from toolbox.api.datagalaxy_api_glossary import DataGalaxyApiGlossary
from toolbox.api.datagalaxy_api_dictionary import DataGalaxyApiDictionary
from toolbox.api.datagalaxy_api_links import DataGalaxyApiLinks
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace


def copy_links(url_source: str,
               url_target: Optional[str],
               token_source: str,
               token_target: Optional[str],
               workspace_source_name: str,
               workspace_target_name: str) -> DataGalaxyBulkResult:
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

    source_usages_api = DataGalaxyApiUsages(
        url=url_source,
        token=token_source,
        workspace=source_workspace
    )
    source_glossary_api = DataGalaxyApiGlossary(
        url=url_source,
        token=token_source,
        workspace=source_workspace
    )
    source_dictionary_api = DataGalaxyApiDictionary(
        url=url_source,
        token=token_source,
        workspace=source_workspace
    )

    # Find all links in source workspace
    source_usages = source_usages_api.list_usages(workspace_source_name, include_links=True)
    source_properties = source_glossary_api.list_properties(workspace_source_name, include_links=True)
    source_sources = source_dictionary_api.list_sources(workspace_source_name, include_links=True)
    source_containers = source_dictionary_api.list_containers(workspace_source_name, include_links=True)
    source_structures = source_dictionary_api.list_structures(workspace_source_name, include_links=True)
    source_fields = source_dictionary_api.list_fields(workspace_source_name, include_links=True)

    # Collecting all links
    links = parse_links(source_usages)
    links += parse_links(source_properties)
    links += parse_links(source_sources)
    links += parse_links(source_containers)
    links += parse_links(source_structures)
    links += parse_links(source_fields)
    logging.info(f'copy-links - {len(links)} links found')

    target_links_api = DataGalaxyApiLinks(
        url=url_target,
        token=token_target,
        workspace=target_workspace
    )

    # Creating links in target workspace
    return target_links_api.bulk_create_links(workspace_name=workspace_target_name, links=links)


def parse_links(objs: list) -> list:
    links = []
    for obj in objs:
        # DPI are ignored since they are handled differently
        if "DataProcessingItem" in obj["typePath"]:
            continue
        for key in obj["links"]:
            for dest in obj["links"][key]:
                if "DataProcessingItem" in dest["typePath"]:
                    continue
                logging.info(f'copy-links - {obj["path"]} {key} {dest["path"]}')
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
