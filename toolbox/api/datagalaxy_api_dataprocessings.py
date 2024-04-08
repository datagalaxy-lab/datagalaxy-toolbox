import logging
import requests as requests
from toolbox.api.datagalaxy_api import DataGalaxyBulkResult, to_bulk_tree


class DataGalaxyApiDataprocessings:
    def __init__(self, url: str, access_token: str, workspace: dict):
        if workspace["isVersioningEnabled"]:
            raise Exception('Workspace with versioning enabled are currently not supported.')
        self.url = url
        self.access_token = access_token
        self.workspace = workspace

    def list_dataprocessings(self, workspace_name: str) -> list:
        version_id = self.workspace['defaultVersionId']
        params = {'versionId': version_id, 'includeAttributes': 'false'}
        headers = {'Authorization': f"Bearer {self.access_token}"}
        response = requests.get(f"{self.url}/dataProcessing", params=params, headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])
        logging.info(
            f'list_dataprocessings - {len(body_json["results"])} dataprocessings found on '
            f'workspace: {workspace_name}')
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

    def list_dataprocessing_items(self, workspace_name: str, parent_id: str) -> list:
        version_id = self.workspace['defaultVersionId']
        params = {'versionId': version_id, 'parentId': parent_id, 'includeAttributes': 'false'}
        headers = {'Authorization': f"Bearer {self.access_token}"}
        response = requests.get(f"{self.url}/dataProcessingItem", params=params, headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])
        logging.info(
            f'list_dataprocessing_items - {len(body_json["results"])} dataprocessingitems found on '
            f'workspace: {workspace_name} for parent_id: {parent_id}')
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

    def bulk_upsert_dataprocessings_tree(self, workspace_name: str, dataprocessings: list) -> DataGalaxyBulkResult:
        # Existing entities are updated and non-existing ones are created.
        bulk_tree = to_bulk_tree(dataprocessings)

        version_id = self.workspace['defaultVersionId']
        headers = {'Authorization': f"Bearer {self.access_token}"}
        response = requests.post(f"{self.url}/dataProcessing/bulktree/{version_id}", json=bulk_tree, headers=headers)
        code = response.status_code
        body_json = response.json()
        if 200 <= code < 300:
            result = DataGalaxyBulkResult(total=body_json["total"], created=body_json["created"],
                                          deleted=body_json["deleted"], unchanged=body_json["unchanged"],
                                          updated=body_json["updated"])
            logging.info(
                f'bulk_upsert_dataprocessings_tree - {result.total} dataprocessings copied on workspace {workspace_name}:'
                f'{result.created} were created, {result.updated} were updated, '
                f'{result.deleted} were deleted and {result.unchanged} were unchanged')
            return result

        if 400 <= code < 500:
            raise Exception(body_json['error'])

        raise Exception(f'Unexpected error, code: {code}')

    def delete_objects(self, workspace_name: str, ids: list) -> DataGalaxyBulkResult:
        if self.workspace["isVersioningEnabled"]:
            raise Exception('Versionned workspaces are not supported')

        version_id = self.workspace['defaultVersionId']
        headers = {'Authorization': f"Bearer {self.access_token}"}
        response = requests.delete(f"{self.url}/dataProcessing/bulk/{version_id}",
                                   json=ids,
                                   headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])
        return body_json
