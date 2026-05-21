import logging
from typing import Optional
from datetime import datetime
from pathlib import Path

from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.http_client import HttpClient
from toolbox.commands.utils import config_workspace, flatten_pages, write_file, create_batches_of_links


def export_links(url: str,
                 token: str,
                 workspace_name: str,
                 version_name: Optional[str],
                 http_client: HttpClient) -> int:
    # Source workspace
    workspace = config_workspace(
        mode="source",
        url=url,
        token=token,
        workspace_name=workspace_name,
        version_name=version_name,
        http_client=http_client
    )
    if not workspace:
        return 1

    # Fetch all objects from source workspace
    glossary_api = DataGalaxyApiModules(
        url=url,
        token=token,
        workspace=workspace,
        module="Glossary",
        http_client=http_client
    )
    dictionary_api = DataGalaxyApiModules(
        url=url,
        token=token,
        workspace=workspace,
        module="Dictionary",
        http_client=http_client
    )
    dataprocessings_api = DataGalaxyApiModules(
        url=url,
        token=token,
        workspace=workspace,
        module="DataProcessing",
        http_client=http_client
    )
    usages_api = DataGalaxyApiModules(
        url=url,
        token=token,
        workspace=workspace,
        module="Uses",
        http_client=http_client
    )

    # Find all links in source workspace
    glossary = glossary_api.list_objects(workspace_name, include_links=True)
    dataprocessings = dataprocessings_api.list_objects(workspace_name, include_links=True)
    usages = usages_api.list_objects(workspace_name, include_links=True)
    dictionary = dictionary_api.list_objects(workspace_name, include_links=True)
    dictionary_children = []
    for page in dictionary:
        for source in page:
            id = source['id']
            containers = dictionary_api.list_children_objects(workspace_name, id, "containers", include_links=True)
            structures = dictionary_api.list_children_objects(workspace_name, id, "structures", include_links=True)
            fields = dictionary_api.list_children_objects(workspace_name, id, "fields", include_links=True)
            dictionary_children += containers
            dictionary_children += structures
            dictionary_children += fields
    # Collecting all links
    link_batches = create_batches_of_links(glossary + dictionary + dataprocessings + usages + dictionary_children)
    count_links = 0
    for batch in link_batches:
        count_links += len(batch)
    logging.info(f"export-links - {count_links} links found")

    # Write file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_dir = Path("export")
    export_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{workspace_name}_links_{timestamp}.json"
    write_file(filename, export_dir, flatten_pages(link_batches))

    return 0


def export_links_parse(subparsers):
    # create the parser for the "export_links" command
    export_links_parse = subparsers.add_parser('export-links', help='export-links help')
    export_links_parse.add_argument(
        '--url',
        type=str,
        help='url source environnement',
        required=True)
    export_links_parse.add_argument(
        '--token',
        type=str,
        help='token source environnement',
        required=True)
    export_links_parse.add_argument(
        '--workspace',
        type=str,
        help='workspace source name',
        required=True)
    export_links_parse.add_argument(
        '--version',
        type=str,
        help='version source name')
