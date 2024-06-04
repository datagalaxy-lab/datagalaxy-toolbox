from toolbox.api.datagalaxy_api import get_access_token, Token, DataGalaxyBulkResult
from toolbox.api.datagalaxy_api_dictionary import DataGalaxyApiDictionary
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
import logging


def delete_dictionary(url: str,
                      token: str,
                      workspace_name: str) -> DataGalaxyBulkResult:

    integration_token = Token(token)
    access_token = get_access_token(url, integration_token)
    workspaces_api = DataGalaxyApiWorkspace(
        url=url,
        access_token=access_token)

    workspace = workspaces_api.get_workspace(workspace_name)

    if not workspace:
        raise Exception(f'workspace {workspace_name} does not exist')

    # on récupère les propriétés du dictionary du workspace_source
    dictionary_api = DataGalaxyApiDictionary(
        url=url,
        access_token=access_token,
        workspace=workspace
    )
    sources = dictionary_api.list_sources(workspace_name)

    ids = list(map(lambda object: object['id'], sources))

    if ids is None or len(ids) < 1:
        logging.warn("Nothing to delete in this module")
        return 0

    return dictionary_api.delete_sources(
        workspace_name=workspace_name,
        ids=ids
    )


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
        help='integration token',
        required=True)
    delete_dictionary_parse.add_argument(
        '--workspace',
        type=str,
        help='workspace name',
        required=True)
