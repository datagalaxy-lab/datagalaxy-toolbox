from dataclasses import dataclass

import jwt
import requests
import logging

logging.basicConfig(level=logging.INFO,
                    format='{asctime} {levelname} {message}',
                    style='{'
                    )


class Token:
    def __init__(self, value):
        self.value = value

    def get_client_space_id(self) -> str:
        decode_token = jwt.decode(
            self.value,
            options={"verify_signature": False},
            algorithms=["HS256"]
        )
        # old auth
        if "cid" in decode_token:
            client_space_id = decode_token["cid"]
        # authv2
        elif "dg_client_id" in decode_token:
            client_space_id = decode_token["dg_client_id"]
        else:
            raise Exception('Error while decoding the token')

        return client_space_id


@dataclass
class DataGalaxyApi:
    url: str
    token: Token


class DataGalaxyApiAuthentication:
    def __init__(self, datagalaxy_api: DataGalaxyApi):
        self.datagalaxy_api = datagalaxy_api

    def authenticate(self) -> str:
        """
        Generate an access token from the DataGalaxy API.

        Documentation: https://apici.datagalaxy.com/v2/documentation/beta#operation/Generate
        :return: an access token
        """
        headers = {"Authorization": f"Bearer {self.datagalaxy_api.token.value}"}
        request = requests.get(f"{self.datagalaxy_api.url}/credentials", headers=headers)
        body_json = request.json()
        code = request.status_code
        if code == 200:
            return body_json['accessToken']
        elif 400 <= code < 500:
            raise Exception(body_json['error'])
        else:
            raise Exception(f'Unexpected error, code: {code}')


def get_access_token(url: str, integration_token: Token):
    dev_uat_env = DataGalaxyApi(url, integration_token)
    auth_api = DataGalaxyApiAuthentication(dev_uat_env)
    access_token = auth_api.authenticate()
    client_space_id = integration_token.get_client_space_id()
    logging.info(f'get_access_token - Authenticating [url: {url} , client_space: {client_space_id}]')
    return access_token


@dataclass(frozen=True)
class DataGalaxyBulkResult:
    total: int
    created: int
    deleted: int
    unchanged: int
    updated: int


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
            if 'lastEntry' in value and value['lastEntry'] is not None:
                # Expected format : "Date::Value"
                last_entry = value['lastEntry']
                if 'date' in last_entry and 'value' in last_entry:
                    property[key] = f"{last_entry['date']}::{last_entry['value']}"


def remove_technology_code(node):
    if 'technologyCode' in node:
        del node['technologyCode']

    if 'children' in node:
        for child in node['children']:
            remove_technology_code(child)


def to_bulk_tree(properties: list) -> list:
    if properties is None or len(properties) == 0:
        logging.warn("Cannot bulk upsert an empty list of objects")
        return 0

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


def prune_tree(tree, target_tag):
    # Function to recursively prune the tree
    def recursive_prune(node):
        if 'children' in node:
            # Recursively prune children
            node['children'] = [child for child in node['children'] if recursive_prune(child)]
            # Keep this node if it has the target tag or any of its children have the tag
            return 'tags' in node and target_tag in node['tags'] or any(recursive_prune(child) for child in node['children'])
        # Keep leaf nodes only if they have the target tag
        return 'tags' in node and target_tag in node['tags']

    # Prune the tree recursively
    pruned_tree = [node for node in tree if recursive_prune(node)]
    return pruned_tree
