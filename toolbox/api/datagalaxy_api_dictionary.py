import logging
import requests as requests
from toolbox.api.datagalaxy_api import DataGalaxyBulkResult, to_bulk_tree


class DataGalaxyApiDictionary:
    def __init__(self, url: str, access_token: str, workspace: dict):
        if workspace["isVersioningEnabled"]:
            raise Exception('Workspace with versioning enabled are currently not supported.')
        self.url = url
        self.access_token = access_token
        self.workspace = workspace

    def list_sources(self, workspace_name: str, include_links=False) -> list:
        version_id = self.workspace['defaultVersionId']
        if include_links is True:
            params = {'versionId': version_id, 'includeAttributes': 'false', 'includeLinks': 'true'}
        else:
            params = {'versionId': version_id, 'includeAttributes': 'true'}
        headers = {'Authorization': f"Bearer {self.access_token}"}
        response = requests.get(f"{self.url}/sources", params=params, headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])

        logging.info(
            f'list_sources - {len(body_json["results"])} sources found on '
            f'workspace: {workspace_name}')
        result = []
        result = result + body_json['results']
        next_page = body_json["next_page"]
        while next_page is not None:
            headers = {'Authorization': f"Bearer {self.access_token}"}
            response = requests.get(next_page, headers=headers)
            body_json = response.json()
            # We can have errors on next page too
            if response.status_code != 200:
                raise Exception(body_json['error'])
            next_page = body_json["next_page"]
            result = result + body_json['results']
        return result

    def list_containers(self, workspace_name: str, include_links=False) -> list:
        version_id = self.workspace['defaultVersionId']
        if include_links is True:
            params = {'versionId': version_id, 'includeAttributes': 'false', 'includeLinks': 'true'}
        else:
            params = {'versionId': version_id, 'includeAttributes': 'true'}
        headers = {'Authorization': f"Bearer {self.access_token}"}
        response = requests.get(f"{self.url}/containers", params=params, headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])

        logging.info(
            f'list_containers - {len(body_json["results"])} containers found on '
            f'workspace: {workspace_name}')
        result = []
        result = result + body_json['results']
        next_page = body_json["next_page"]
        while next_page is not None:
            headers = {'Authorization': f"Bearer {self.access_token}"}
            response = requests.get(next_page, headers=headers)
            body_json = response.json()
            # We can have errors on next page too
            if response.status_code != 200:
                raise Exception(body_json['error'])
            next_page = body_json["next_page"]
            result = result + body_json['results']
        return result

    def list_structures(self, workspace_name: str, include_links=False) -> list:
        version_id = self.workspace['defaultVersionId']
        if include_links is True:
            params = {'versionId': version_id, 'includeAttributes': 'false', 'includeLinks': 'true'}
        else:
            params = {'versionId': version_id, 'includeAttributes': 'true'}
        headers = {'Authorization': f"Bearer {self.access_token}"}
        response = requests.get(f"{self.url}/structures", params=params, headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])

        logging.info(
            f'list_structures - {len(body_json["results"])} structures found on '
            f'workspace: {workspace_name}')
        result = []
        result = result + body_json['results']
        next_page = body_json["next_page"]
        while next_page is not None:
            headers = {'Authorization': f"Bearer {self.access_token}"}
            response = requests.get(next_page, headers=headers)
            body_json = response.json()
            # We can have errors on next page too
            if response.status_code != 200:
                raise Exception(body_json['error'])
            next_page = body_json["next_page"]
            result = result + body_json['results']
        return result

    def list_fields(self, workspace_name: str, include_links=False) -> list:
        version_id = self.workspace['defaultVersionId']
        if include_links is True:
            params = {'versionId': version_id, 'includeAttributes': 'false', 'includeLinks': 'true'}
        else:
            params = {'versionId': version_id, 'includeAttributes': 'true'}
        headers = {'Authorization': f"Bearer {self.access_token}"}
        response = requests.get(f"{self.url}/fields", params=params, headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])

        logging.info(
            f'list_fields - {len(body_json["results"])} fields found on '
            f'workspace: {workspace_name}')
        result = []
        result = result + body_json['results']
        next_page = body_json["next_page"]
        while next_page is not None:
            headers = {'Authorization': f"Bearer {self.access_token}"}
            response = requests.get(next_page, headers=headers)
            body_json = response.json()
            # We can have errors on next page too
            if response.status_code != 200:
                raise Exception(body_json['error'])
            next_page = body_json["next_page"]
            result = result + body_json['results']
        return result

    def bulk_upsert_sources_tree(self, workspace_name: str, sources: list) -> DataGalaxyBulkResult:
        # Existing entities are updated and non-existing ones are created.
        bulk_tree = to_bulk_tree(sources)

        # We need to make a post request for each source tree
        for source_bulk in bulk_tree:
            # We cannot send a bulktree containing only a source without children (rejected by the API)
            if 'children' not in source_bulk or len(source_bulk['children']) < 1:
                logging.warn(f'bulk_upsert_sources_tree - Cannot create a source without children : {source_bulk}')
                continue

            version_id = self.workspace['defaultVersionId']
            headers = {'Authorization': f"Bearer {self.access_token}"}
            response = requests.post(f"{self.url}/sources/bulktree/{version_id}", json=source_bulk,
                                     headers=headers)
            code = response.status_code
            body_json = response.json()
            if 200 <= code < 300:
                result = DataGalaxyBulkResult(total=body_json["total"], created=body_json["created"],
                                              deleted=body_json["deleted"], unchanged=body_json["unchanged"],
                                              updated=body_json["updated"])
                logging.info(
                    f'bulk_upsert_sources_tree - {result.total} sources copied on workspace {workspace_name}:'
                    f'{result.created} were created, {result.updated} were updated, '
                    f'{result.deleted} were deleted and {result.unchanged} were unchanged')
                logging.info(result)

            if 400 <= code < 500:
                raise Exception(body_json['error'])

        return 200

    def delete_sources(self, workspace_name: str, ids: list) -> DataGalaxyBulkResult:
        if self.workspace["isVersioningEnabled"]:
            raise Exception('Versionned workspaces are not supported')

        version_id = self.workspace['defaultVersionId']
        headers = {'Authorization': f"Bearer {self.access_token}"}
        response = requests.delete(f"{self.url}/sources/bulk/{version_id}",
                                   json=ids,
                                   headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])
        return body_json
