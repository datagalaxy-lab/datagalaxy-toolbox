import logging
from typing import Optional
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
from toolbox.api.http_client import HttpClient


def config_workspace(mode: str, url: str, token: str, workspace_name: str, version_name: Optional[str], http_client: HttpClient):
    workspaces_api = DataGalaxyApiWorkspace(
        url=url,
        token=token,
        http_client=http_client)
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


def create_batches_of_links(input_arrays, max_size=5000):
    batches = []  # This will hold the list of arrays
    current_batch = []  # Temporary array to build chunks

    for arr in input_arrays:
        for obj in arr:  # Add each object from the input array
            links = parse_links(obj)
            if len(current_batch) < max_size:
                current_batch += links
            else:
                # When the current array reaches max size, save it and start a new one
                batches.append(current_batch)
                current_batch = links

    # Add the remaining objects in `current_batch` if it's not empty
    if current_batch:
        batches.append(current_batch)

    return batches


def parse_links(obj: dict) -> list:
    links = []
    # DPI are ignored since they are handled differently
    if "DataProcessingItem" in obj["typePath"]:
        return []
    # ReferenceDataValue have to be ignored (at least for now)
    if "ReferenceDataValue" in obj["typePath"]:
        return []
    for key in obj["links"]:
        for dest in obj["links"][key]:
            if "DataProcessingItem" in dest["typePath"]:
                continue
            if "ReferenceDataValue" in dest["typePath"]:
                logging.warning('The following link cannot be created with the API, please create it manually:')
                logging.warning(obj["path"])
                logging.warning(obj["typePath"])
                logging.warning(key)
                logging.warning(dest["path"])
                logging.warning(dest["typePath"])
                continue
            link = {
                    'fromPath': obj["path"],
                    'fromType': obj["typePath"],
                    'linkType': key,
                    'toPath': dest["path"],
                    'toType': dest["typePath"]
                    }
            links.append(link)
    return links
