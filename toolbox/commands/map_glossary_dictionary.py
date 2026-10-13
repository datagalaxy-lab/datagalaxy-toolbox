import csv
import logging
from pathlib import Path
from typing import Optional

from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.http_client import HttpClient
from toolbox.commands.utils import config_workspace


def map_glossary_dictionary(
                            url: str,
                            token: str,
                            workspace_name: str,
                            version_name: Optional[str],
                            file_path: str,
                            glossary_column: str,
                            dictionary_column: str,
                            http_client: HttpClient) -> int:
    workspace = config_workspace(
        mode="target",
        url=url,
        token=token,
        workspace_name=workspace_name,
        version_name=version_name,
        http_client=http_client
    )
    if not workspace:
        return 1

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

    link_api = DataGalaxyApiModules(
        url=url,
        token=token,
        workspace=workspace,
        module="Links",
        http_client=http_client
    )

    mapping_file = Path(file_path)
    if not mapping_file.exists():
        logging.warning(f'map-glossary-dictionary - No mapping file found at {mapping_file}, aborting.')
        return 1
    with open(mapping_file, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    logging.info(f"map-glossary-dictionary - Mapping file loaded successfully ({len(rows)} rows)")

    links = []
    for row in rows:
        glossary_name = row[glossary_column].strip()
        dictionary_name = row[dictionary_column].strip()
        if not glossary_name or not dictionary_name:
            continue

        # Find glossary objects
        glossary_objects = glossary_api.list_objects(workspace_name, glossary_name)
        if not glossary_objects:
            logging.warning(f'map-glossary-dictionary - Glossary object "{glossary_name}" not found, skipping.')
            continue

        # Find dictionary objects
        dictionary_objects = dictionary_api.list_children_objects(workspace_name, workspace['id'], "fields", dictionary_name)
        if not dictionary_objects:
            logging.warning(f'map-glossary-dictionary - Dictionary object "{dictionary_name}" not found, skipping.')
            continue

        for glossary_page in glossary_objects:
            for glossary_object in glossary_page:
                for dictionary_page in dictionary_objects:
                    for dictionary_object in dictionary_page:
                        links.append({
                            "fromId": glossary_object['id'],
                            "toId": dictionary_object['id'],
                            "type": "IsImplementedBy"
                        })

    for start in range(0, len(links), 5000):
        link_api.bulk_upsert_tree(
            workspace_name=workspace_name,
            bulktree=links[start:start + 5000],
            links_by_id=True,
            tag_value=None
        )
    return 0


# Parsers
def map_glossary_dictionary_parse(subparsers):
    # create the parser for the "map_glossary_dictionary" command
    map_glossary_dictionary_parse = subparsers.add_parser('map-glossary-dictionary', help='map-glossary-dictionary help')
    map_glossary_dictionary_parse.add_argument(
        '--url',
        type=str,
        help='url environnement',
        required=True)
    map_glossary_dictionary_parse.add_argument(
        '--token',
        type=str,
        help='token environnement',
        required=True)
    map_glossary_dictionary_parse.add_argument(
        '--workspace',
        type=str,
        help='workspace name',
        required=True)
    map_glossary_dictionary_parse.add_argument(
        '--version',
        type=str,
        help='version name')
    map_glossary_dictionary_parse.add_argument(
        '--file-path',
        type=str,
        help='path to the CSV file',
        required=True)
    map_glossary_dictionary_parse.add_argument(
        '--glossary-column',
        type=str,
        help='CSV column holding the glossary object name',
        default='Libellé fonctionnel')
    map_glossary_dictionary_parse.add_argument(
        '--dictionary-column',
        type=str,
        help='CSV column holding the dictionary object name',
        default='Identifiant')
