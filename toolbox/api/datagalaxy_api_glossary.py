import logging
import requests as requests
from toolbox.api.datagalaxy_api import DataGalaxyBulkResult, to_bulk_tree, prune_tree
from typing import Optional


class DataGalaxyApiGlossary:
    def __init__(self, url: str, access_token: str, workspace: dict):
        self.url = url
        self.access_token = access_token
        self.workspace = workspace

    def list_properties(self, workspace_name: str, include_links=False) -> list:
        if not self.workspace["isVersioningEnabled"]:
            version_id = self.workspace['defaultVersionId']
            if include_links is True:
                params = {'versionId': version_id, 'includeAttributes': 'false', 'includeLinks': 'true'}
            else:
                params = {'versionId': version_id, 'includeAttributes': 'true'}
            headers = {'Authorization': f"Bearer {self.access_token}"}
            response = requests.get(f"{self.url}/properties", params=params, headers=headers)
            code = response.status_code
            body_json = response.json()
            if code == 200:
                logging.info(
                    f'list_properties - {len(body_json["results"])} properties found on '
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

    def bulk_upsert_property_tree(self, workspace_name: str, properties: list, tag_value: Optional[str]) -> DataGalaxyBulkResult:
        # Existing entities are updated and non-existing ones are created.
        properties_ok_to_bulk = to_bulk_tree(properties)

        if tag_value is not None:
            properties_ok_to_bulk = prune_tree(properties_ok_to_bulk, tag_value)

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

    def delete_objects(self, workspace_name: str, ids: list) -> DataGalaxyBulkResult:
        if self.workspace["isVersioningEnabled"]:
            raise Exception('Versionned workspaces are not supported')

        version_id = self.workspace['defaultVersionId']
        headers = {'Authorization': f"Bearer {self.access_token}"}
        response = requests.delete(f"{self.url}/properties/bulk/{version_id}",
                                   json=ids,
                                   headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])
        return body_json
