import logging
from dataclasses import dataclass

import requests as requests


@dataclass(frozen=True)
class DataGalaxyBulkResult:
    total: int
    created: int
    deleted: int
    unchanged: int
    updated: int


class DataGalaxyApiWorkspace:
    def __init__(self, url: str, access_token: str):
        self.url = url
        self.access_token = access_token

    def list_workspaces(self):
        headers = {'Authorization': f"Bearer {self.access_token}"}
        response = requests.get(f"{self.url}/workspaces", headers=headers)
        code = response.status_code
        body_json = response.json()
        if code == 200:
            workspaces = []
            for workspace in body_json["projects"]:
                workspaces.append(workspace)
            return workspaces

        if 400 <= code < 500:
            raise Exception(body_json['error'])

        raise Exception(f'Unexpected error, code: {code}')

    def get_workspace(self, name: str) -> dict:
        workspaces = []
        for workspace in self.list_workspaces():
            workspaces.append(workspace['name'])
            if workspace['name'] == name:
                return workspace

        raise Exception(f'Workspace {name} does not exist, workspaces found: {workspaces}')


class DataGalaxyApiGlossary:
    def __init__(self, url: str, access_token: str, workspace: dict):
        self.url = url
        self.access_token = access_token
        self.workspace = workspace

    def list_glossary_properties(self, workspace_name: str) -> list:
        if not self.workspace["isVersioningEnabled"]:
            version_id = self.workspace['defaultVersionId']
            params = {'versionId': version_id, 'includeAttributes': 'true'}
            headers = {'Authorization': f"Bearer {self.access_token}"}
            response = requests.get(f"{self.url}/properties", params=params, headers=headers)
            code = response.status_code
            body_json = response.json()
            if code == 200:
                logging.info(
                    f'list_glossary_properties - {len(body_json["results"])} properties found on '
                    f'workspace {workspace_name} :')
                result = []
                result = result + body_json['results']
                next_page = body_json["next_page"]
                while next_page is not None:
                    headers = {'Authorization': f"Bearer {self.access_token}"}
                    response = requests.get(next_page, headers=headers)
                    body_json = response.json()
                    next_page = body_json["next_page"]
                    result = result + body_json['results']
                return result

            if 400 <= code < 500:
                raise Exception(body_json['error'])

            raise Exception(f'Unexpected error, code: {code}')

        elif self.workspace["isVersioningEnabled"]:
            raise Exception('pour l instant on ne gere pas le versioning')

    def bulk_upsert_property_tree(self, workspace_name: str, properties: list) -> DataGalaxyBulkResult:
        # Existing entities are updated and non-existing ones are created.
        properties_ok_to_bulk = to_bulk_tree(properties)
        logging.info(f'properties_ok_to_bulk: {properties_ok_to_bulk}')

        if not self.workspace["isVersioningEnabled"]:
            version_id = self.workspace['defaultVersionId']
            headers = {'Authorization': f"Bearer {self.access_token}"}
            response = requests.post(f"{self.url}/properties/bulktree/{version_id}", json=properties_ok_to_bulk,
                                     headers=headers)
            code = response.status_code
            body_json = response.json()
            if 200 <= code < 300:
                result = DataGalaxyBulkResult(total=body_json["total"], created=body_json["created"],
                                              deleted=body_json["deleted"], unchanged=body_json["unchanged"],
                                              updated=body_json["updated"])
                logging.info(
                    f'bulk_upsert_property_tree - {result.total} properties copied on workspace {workspace_name}:'
                    f'{result.created} were created, {result.updated} were updated, '
                    f'{result.deleted} were deleted and {result.unchanged} were unchanged')
                return result

            if 400 <= code < 500:
                raise Exception(body_json['error'])

            raise Exception(f'Unexpected error, code: {code}')

        elif self.workspace["isVersioningEnabled"]:
            raise Exception('pour l instant on ne sait pas si on accepte le versioning')


BULK_PROPERTIES_FIELDS_TO_REMOVE = ['path', 'typePath', 'location', 'attributes', 'objectUrl', 'childrenCount',
                                    'lastModificationTime', 'creationTime']


def del_useless_keys(members: dict):
    for key in list(members.keys()):
        if key in BULK_PROPERTIES_FIELDS_TO_REMOVE:
            del members[key]
        else:
            pass

    return members


PATH_SEPARATOR = "\\"


@dataclass(frozen=True)
class DataGalaxyPathWithType:
    path: str
    path_type: str


def handle_timeserie(property: dict) -> dict:
    # Temporary solution: only copy the latest value of the TimeSerie
    for key, value in property.items():
        if isinstance(value, dict):
            if 'lastEntry' in value:
                # Expected format : "Date::Value"
                property[key] = f"{value['lastEntry']['date']}::{value['lastEntry']['value']}"


def to_bulk_tree(properties: list) -> list:
    nodes_map = {}
    for property in properties:
        nodes_map[DataGalaxyPathWithType(property['path'], property['typePath'])] = property

    for property in properties:

        if 'attributes' in property:
            property.update(property['attributes'])

        path = property['path']
        path_type = property['typePath']
        del_useless_keys(property)
        handle_timeserie(property)

        # TRANSFORM to bulk item
        path_segments = path[1:].split(PATH_SEPARATOR)
        if len(path_segments) > 1:
            parent_path_segments = path_segments[:-1]
            parent_path_type_segments = path_type[1:].split(PATH_SEPARATOR)[:-1]
            parent_path = f"{PATH_SEPARATOR}{PATH_SEPARATOR.join(parent_path_segments)}"
            parent_path_type = f"{PATH_SEPARATOR}{PATH_SEPARATOR.join(parent_path_type_segments)}"
            parent = nodes_map[DataGalaxyPathWithType(parent_path, parent_path_type)]
            if 'children' in parent:
                parent['children'].append(property)
            else:
                parent['children'] = [property]

    root_nodes = []
    for key, value in nodes_map.items():
        if len(key.path[1:].split(PATH_SEPARATOR)) == 1:
            root_nodes.append(value)

    return root_nodes
