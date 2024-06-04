from toolbox.api.datagalaxy_api import get_access_token, Token, DataGalaxyBulkResult
from toolbox.api.datagalaxy_api_usages import DataGalaxyApiUsages
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
import logging


def delete_usages(url: str,
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

    # on récupère les propriétés du usages du workspace_source
    usages_api = DataGalaxyApiUsages(
        url=url,
        access_token=access_token,
        workspace=workspace
    )
    usages = usages_api.list_usages(workspace_name)

    ids = list(map(lambda object: object['id'], usages))

    if ids is None or len(ids) < 1:
        logging.warn("Nothing to delete in this module")
        return 0

    return usages_api.delete_objects(
        workspace_name=workspace_name,
        ids=ids
    )


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
        help='integration token',
        required=True)
    delete_usages_parse.add_argument(
        '--workspace',
        type=str,
        help='workspace name',
        required=True)
