import logging
import requests as requests
from toolbox.api.datagalaxy_api import DataGalaxyBulkResult, to_bulk_tree


def remove_technology_code(node):
    if 'technologyCode' in node:
        del node['technologyCode']

    if 'children' in node:
        for child in node['children']:
            remove_technology_code(child)


class DataGalaxyApiUsages:
    def __init__(self, url: str, access_token: str, workspace: dict):
        self.url = url
        self.access_token = access_token
        self.workspace = workspace

    def list_usages(self, workspace_name: str) -> list:
        if not self.workspace["isVersioningEnabled"]:
            version_id = self.workspace['defaultVersionId']
            params = {'versionId': version_id, 'includeAttributes': 'true'}
            headers = {'Authorization': f"Bearer {self.access_token}"}
            response = requests.get(f"{self.url}/usages", params=params, headers=headers)
            code = response.status_code
            body_json = response.json()
            if code == 200:
                logging.info(
                    f'list_usages - {len(body_json["results"])} usages found on '
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

            if 400 <= code < 500:
                raise Exception(body_json['error'])

            raise Exception(f'Unexpected error, code: {code}')

        raise Exception('Workspace with versioning enabled are currently not supported.')

    def bulk_upsert_usages_tree(self, workspace_name: str, usages: list) -> DataGalaxyBulkResult:
        # Existing entities are updated and non-existing ones are created.
        usages_ok_to_bulk = to_bulk_tree(usages)
        logging.info(f'usages_ok_to_bulk: {usages_ok_to_bulk}')

        # If a parent usage has a technology, it is necessary to delete the "technologyCode" property in every children
        # Otherwise the API returns an error. Only the parent can hold the "technologyCode" property
        for usage_tree in usages_ok_to_bulk:
            if 'technologyCode' in usage_tree:
                for children in usage_tree['children']:
                    remove_technology_code(children)

        if not self.workspace["isVersioningEnabled"]:
            version_id = self.workspace['defaultVersionId']
            headers = {'Authorization': f"Bearer {self.access_token}"}
            response = requests.post(f"{self.url}/usages/bulktree/{version_id}", json=usages_ok_to_bulk,
                                     headers=headers)
            code = response.status_code
            body_json = response.json()
            if 200 <= code < 300:
                result = DataGalaxyBulkResult(total=body_json["total"], created=body_json["created"],
                                              deleted=body_json["deleted"], unchanged=body_json["unchanged"],
                                              updated=body_json["updated"])
                logging.info(
                    f'bulk_upsert_usages_tree - {result.total} usages copied on workspace {workspace_name}:'
                    f'{result.created} were created, {result.updated} were updated, '
                    f'{result.deleted} were deleted and {result.unchanged} were unchanged')
                return result

            if 400 <= code < 500:
                raise Exception(body_json['error'])

            raise Exception(f'Unexpected error, code: {code}')

        raise Exception('Workspace with versioning enabled are currently not supported.')
