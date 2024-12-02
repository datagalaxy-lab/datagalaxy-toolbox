from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
from toolbox.api.datagalaxy_api import find_root_objects


def delete_dictionary(url: str,
                      token: str,
                      workspace_name: str) -> int:

    workspaces_api = DataGalaxyApiWorkspace(
        url=url,
        token=token)

    workspace = workspaces_api.get_workspace(workspace_name)

    if not workspace:
        raise Exception(f'workspace {workspace_name} does not exist')

    # fetching objects from source workspace
    module_api = DataGalaxyApiModules(
        url=url,
        token=token,
        workspace=workspace,
        module="Dictionary"
    )
    objects = module_api.list_objects(
        workspace_name)

    for page in objects:
        root_objects = find_root_objects(page)
        ids = list(map(lambda object: object['id'], root_objects))
        module_api.delete_objects(
            workspace_name=workspace_name,
            ids=ids
        )

    return 0


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
