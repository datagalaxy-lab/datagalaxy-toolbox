import logging
from typing import Optional
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace


def config_workspace(mode: str, url: str, token: str, workspace_name: str, version_name: Optional[str]):
    workspaces_api = DataGalaxyApiWorkspace(
        url=url,
        token=token)
    workspace = workspaces_api.get_workspace(workspace_name)
    if not workspace:
        return None
    logging.info(f'config_workspace - Found {mode} workspace {workspace_name}')
    if version_name is None:
        if workspace["isVersioningEnabled"]:
            logging.error(f'config_workspace - Versioning is enabled for {mode} workspace {workspace_name}, please specify the version name')
            return None
        else:
            workspace['versionId'] = workspace['defaultVersionId']
    else:
        if not workspace["isVersioningEnabled"]:
            logging.warn(f'config_workspace - Versioning is not enabled for {mode} workspace {workspace_name}, ignoring this parameter')
            workspace['versionId'] = workspace['defaultVersionId']
        else:
            version = workspaces_api.get_version(workspace['id'], version_name)
            if not version:
                return None
            workspace['versionId'] = version['versionId']
            logging.info(f'config_workspace - Found version {version_name} with id {version["versionId"]} for {mode} workspace {workspace_name}')
    return workspace
