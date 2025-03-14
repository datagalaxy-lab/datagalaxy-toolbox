from typing import Optional

from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.datagalaxy_api import find_root_objects
from toolbox.commands.utils import config_workspace


def delete_module(module: str,
                  url: str,
                  token: str,
                  workspace_name: str,
                  version_name: Optional[str]) -> str:

    # Workspace
    workspace = config_workspace(
        mode="target",
        url=url,
        token=token,
        workspace_name=workspace_name,
        version_name=version_name
    )
    if not workspace:
        return 1

    # Target module
    module_api = DataGalaxyApiModules(
        url=url,
        token=token,
        workspace=workspace,
        module=module
    )

    # Fetch objects from source workspace
    objects = module_api.list_objects(workspace_name)

    for page in objects:
        root_objects = find_root_objects(page)
        ids = list(map(lambda object: object['id'], root_objects))
        module_api.delete_objects(
            workspace_name=workspace_name,
            ids=ids
        )

    return 0


def delete_glossary_parse(subparsers):
    # create the parser for the "delete_glossary" command
    delete_glossary_parse = subparsers.add_parser('delete-glossary', help='delete-glossary help')
    delete_glossary_parse.add_argument(
        '--url',
        type=str,
        help='url environnement',
        required=True)
    delete_glossary_parse.add_argument(
        '--token',
        type=str,
        help='token',
        required=True)
    delete_glossary_parse.add_argument(
        '--workspace',
        type=str,
        help='workspace name',
        required=True)
    delete_glossary_parse.add_argument(
        '--version',
        type=str,
        help='version name')


def delete_dictionary_parse(subparsers):
    # create the parser for the "delete_dictionary" command
    delete_dictionary_parse = subparsers.add_parser('delete-dictionary', help='delete-dictionary help')
    delete_dictionary_parse.add_argument(
        '--url',
        type=str,
        help='url environnement',
        required=True)
    delete_dictionary_parse.add_argument(
        '--token',
        type=str,
        help='token',
        required=True)
    delete_dictionary_parse.add_argument(
        '--workspace',
        type=str,
        help='workspace name',
        required=True)
    delete_dictionary_parse.add_argument(
        '--version',
        type=str,
        help='version name')


def delete_dataprocessings_parse(subparsers):
    # create the parser for the "delete_dataprocessings" command
    delete_dataprocessings_parse = subparsers.add_parser('delete-dataprocessings', help='delete-dataprocessings help')
    delete_dataprocessings_parse.add_argument(
        '--url',
        type=str,
        help='url environnement',
        required=True)
    delete_dataprocessings_parse.add_argument(
        '--token',
        type=str,
        help='token',
        required=True)
    delete_dataprocessings_parse.add_argument(
        '--workspace',
        type=str,
        help='workspace name',
        required=True)
    delete_dataprocessings_parse.add_argument(
        '--version',
        type=str,
        help='version name')


def delete_usages_parse(subparsers):
    # create the parser for the "delete_usages" command
    delete_usages_parse = subparsers.add_parser('delete-usages', help='delete-usages help')
    delete_usages_parse.add_argument(
        '--url',
        type=str,
        help='url environnement',
        required=True)
    delete_usages_parse.add_argument(
        '--token',
        type=str,
        help='token',
        required=True)
    delete_usages_parse.add_argument(
        '--workspace',
        type=str,
        help='workspace name',
        required=True)
    delete_usages_parse.add_argument(
        '--version',
        type=str,
        help='version name')
