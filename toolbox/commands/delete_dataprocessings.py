from toolbox.api.datagalaxy_api import DataGalaxyBulkResult
from toolbox.api.datagalaxy_api_dataprocessings import DataGalaxyApiDataprocessings
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
import logging


def delete_dataprocessings(url: str,
                           token: str,
                           workspace_name: str) -> DataGalaxyBulkResult:

    workspaces_api = DataGalaxyApiWorkspace(
        url=url,
        token=token)

    workspace = workspaces_api.get_workspace(workspace_name)

    if not workspace:
        raise Exception(f'workspace {workspace_name} does not exist')

    # on récupère les propriétés du dataprocessings du workspace_source
    dataprocessings_api = DataGalaxyApiDataprocessings(
        url=url,
        token=token,
        workspace=workspace
    )
    dataprocessings = dataprocessings_api.list_dataprocessings(
        workspace_name)

    ids = list(map(lambda object: object['id'], dataprocessings))

    if ids is None or len(ids) < 1:
        logging.warn("Nothing to delete in this module")
        return 0

    return dataprocessings_api.delete_objects(
        workspace_name=workspace_name,
        ids=ids
    )


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
