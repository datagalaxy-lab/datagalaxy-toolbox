import requests as requests
from toolbox.api.datagalaxy_api import DataGalaxyBulkResult


class DataGalaxyApiLinks:
    def __init__(self, url: str, access_token: str, workspace: dict):
        self.url = url
        self.access_token = access_token
        self.workspace = workspace

    def bulk_create_links(self, workspace_name: str, links: list) -> DataGalaxyBulkResult:
        # Creating links between entities based on their path
        if self.workspace["isVersioningEnabled"]:
            raise Exception('Workspace with versioning enabled are currently not supported.')

        version_id = self.workspace['defaultVersionId']
        headers = {'Authorization': f"Bearer {self.access_token}"}
        response = requests.post(f"{self.url}/links/bulktree/{version_id}", json=links,
                                 headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 201:
            raise Exception(body_json['error'])

        result = DataGalaxyBulkResult(total=body_json["total"],
                                      created=body_json["created"],
                                      deleted=body_json["deleted"],
                                      unchanged=body_json["unchanged"],
                                      updated=body_json["updated"])
        return result
