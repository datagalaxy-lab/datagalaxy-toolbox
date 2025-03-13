import logging
import requests as requests
from toolbox.api.datagalaxy_api import build_bulktree, prune_tree, remove_technology_code, create_batches
from typing import Optional


class DataGalaxyApiModules:
    def __init__(self, url: str, token: str, workspace: dict, module: str):
        if module not in ["Glossary", "Dictionary", "DataProcessing", "Uses", "Links"]:
            raise Exception('The specified module does not exist.')
        self.module = module
        if module == "Glossary":
            self.route = "properties"
        if module == "Dictionary":
            self.route = "sources"
        if module == "DataProcessing":
            self.route = "dataProcessing"
        if module == "Uses":
            self.route = "usages"
        if module == "Links":
            self.route = "links"

        self.url = url
        self.token = token
        self.workspace = workspace

    def list_objects(self, workspace_name: str, include_links=False) -> list:
        version_id = self.workspace['versionId']
        params = {'versionId': version_id, 'limit': '5000'}
        if include_links is True:
            params['includeLinks'] = 'true'
        else:
            params['includeAttributes'] = 'true'
        headers = {'Authorization': f"Bearer {self.token}"}
        response = requests.get(f"{self.url}/{self.route}", params=params, headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])
        logging.info(
            f'list_objects - {len(body_json["results"])} objects found on '
            f'workspace "{workspace_name}" in module {self.module}')
        result_pages = [body_json['results']]
        next_page = body_json["next_page"]
        while next_page is not None:
            logging.info('Fetching another page from the API...')
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.get(next_page, headers=headers)
            body_json = response.json()
            logging.info(
                f'list_objects - {len(body_json["results"])} objects found on '
                f'workspace "{workspace_name}" in module {self.module}')
            next_page = body_json["next_page"]
            result_pages.append(body_json['results'])
        return result_pages

    # This is a specific request for dataProcessing items
    def list_object_items(self, workspace_name: str, parent_id: str) -> list:
        if self.module != "DataProcessing":
            raise Exception(f'This method is not available for the module {self.module}')

        version_id = self.workspace['versionId']
        params = {'versionId': version_id, 'parentId': parent_id, 'includeAttributes': 'true'}
        headers = {'Authorization': f"Bearer {self.token}"}
        response = requests.get(f"{self.url}/dataProcessingItem", params=params, headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])
        result = []
        result = result + body_json['results']
        next_page = body_json["next_page"]
        while next_page is not None:
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.get(next_page, headers=headers)
            body_json = response.json()
            next_page = body_json["next_page"]
            result = result + body_json['results']
        return result

    # This is a specific request for Dictionary
    def list_children_objects(self, workspace_name: str, parent_id: str, object_type: str, include_links=False) -> list:
        if object_type not in ["containers", "structures", "fields"]:
            raise Exception('The specified object type does not exist.')

        version_id = self.workspace['versionId']
        if include_links is True:
            params = {'versionId': version_id, 'limit': '5000', 'includeLinks': 'true', 'parentId': parent_id}
        else:
            params = {'versionId': version_id, 'limit': '5000', 'includeAttributes': 'true', 'parentId': parent_id}
        headers = {'Authorization': f"Bearer {self.token}"}
        response = requests.get(f"{self.url}/{object_type}", params=params, headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])
        logging.info(
            f'list_children_objects - {len(body_json["results"])} objects found on '
            f'workspace: {workspace_name} of type: {object_type} in module {self.module}')
        result_pages = [body_json['results']]
        next_page = body_json["next_page"]
        while next_page is not None:
            logging.info('Fetching another page from the API...')
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.get(next_page, headers=headers)
            body_json = response.json()
            logging.info(
                f'list_children_objects - {len(body_json["results"])} objects found on '
                f'workspace: {workspace_name} of type: {object_type} in module {self.module}')
            next_page = body_json["next_page"]
            result_pages.append(body_json['results'])
        return result_pages

    # This is a specific request for Dictionary
    def list_keys(self, workspace_name: str, source_id: str, mode: str) -> list:
        if mode not in ['primary', 'foreign']:
            raise Exception("Mode not found")

        version_id = self.workspace['versionId']
        headers = {'Authorization': f"Bearer {self.token}"}
        response = requests.get(f"{self.url}/{self.route}/{version_id}/{source_id}/{mode}Keys", headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])
        logging.info(
            f'list_keys - {len(body_json)} {mode} keys found on '
            f'workspace: {workspace_name} for source {source_id}')
        return body_json

    # This is a specific request for Dictionary
    def create_keys(self, workspace_name: str, source_id: str, keys: list, mode='str') -> int:
        if mode not in ['primary', 'foreign']:
            raise Exception("Mode not found")

        version_id = self.workspace['versionId']
        headers = {'Authorization': f"Bearer {self.token}"}
        response = requests.put(f"{self.url}/{self.route}/{version_id}/{source_id}/{mode}Keys", json=keys, headers=headers)
        code = response.status_code
        body_json = response.json()
        if 200 <= code < 300:
            logging.info(f'create_key - {mode} keys - {body_json}')
        if 400 <= code < 500:
            raise Exception(body_json['error'])

        return 0

    # This is a specific request for Dictionary
    def create_source(self, workspace_name: str, source: dict) -> str:
        version_id = self.workspace['versionId']
        headers = {'Authorization': f"Bearer {self.token}"}
        response = requests.post(f"{self.url}/{self.route}/{version_id}", json=source, headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 201:
            raise Exception(body_json['error'])

        source_id = body_json['id']
        logging.info(f'create_source - Created source {source["name"]} with id {source_id}')

        return source_id

    def bulk_upsert_tree(self, workspace_name: str, objects: list, tag_value: Optional[str]) -> int:
        # Objects can be in pages, so one POST request per page
        for page in objects:
            # Existing entities are updated and non-existing ones are created.
            bulktree = build_bulktree(page)

            if tag_value is not None:
                bulktree = prune_tree(bulktree, tag_value)

            # If a parent usage has a technology, it is necessary to delete the "technologyCode" property in every children
            # Otherwise the API returns an error. Only the parent can hold the "technologyCode" property
            for tree in bulktree:
                if 'children' in tree:
                    for children in tree['children']:
                        remove_technology_code(children)

            version_id = self.workspace['versionId']
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.post(f"{self.url}/{self.route}/bulktree/{version_id}", json=bulktree, headers=headers)
            code = response.status_code
            body_json = response.json()
            if 200 <= code < 300:
                logging.info(f'bulk_upsert_tree - {body_json}')
            if 400 <= code < 500:
                raise Exception(body_json['error'])

        return 200

    # This is a specific request for Dictionary
    def bulk_upsert_source_tree(self, workspace_name: str, source: dict, objects: list, tag_value: Optional[str]) -> int:
        batches = create_batches(objects)

        # One bulktree call per batch
        for batch in batches:
            bulktree = build_bulktree([source] + batch)
            if len(bulktree) > 1:
                raise Exception(f"Problem while creating the bulktree for source {source['name']}")
            bulktree = bulktree[0]

            if tag_value is not None:
                bulktree = prune_tree(bulktree, tag_value)

            version_id = self.workspace['versionId']
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.post(f"{self.url}/{self.route}/bulktree/{version_id}", json=bulktree, headers=headers)
            code = response.status_code
            body_json = response.json()
            if 200 <= code < 300:
                logging.info(f'bulk_upsert_tree - {body_json}')
            if 400 <= code < 500:
                raise Exception(body_json['error'])

        return 200

    def delete_objects(self, workspace_name: str, ids: list) -> int:
        if len(ids) < 1:
            logging.warning(f'Nothing to delete on workspace "{workspace_name}" in module {self.module}, aborting.')
            return 0
        version_id = self.workspace['versionId']
        headers = {'Authorization': f"Bearer {self.token}"}
        response = requests.delete(f"{self.url}/{self.route}/bulk/{version_id}",
                                   json=ids,
                                   headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])
        logging.info(
            f'delete_objects - {body_json["totalDeleted"]} objects were deleted on workspace "{workspace_name}" in module {self.module}')
        return 0

    def bulk_create_links(self, workspace_name: str, links: list) -> int:
        # Objects can be in pages, so one POST request per page
        for page in links:
            version_id = self.workspace['versionId']
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.post(f"{self.url}/{self.route}/bulktree/{version_id}", json=page,
                                     headers=headers)
            code = response.status_code
            body_json = response.json()
            if code != 201:
                raise Exception(body_json['error'])
            logging.info(f"bulk_create_links - {body_json}")
        return 201
