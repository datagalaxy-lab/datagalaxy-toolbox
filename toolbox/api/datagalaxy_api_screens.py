from typing import Optional
from .http_client import HttpClient


class DataGalaxyApiScreen:
    def __init__(self, url: str, token: str, workspace: Optional[dict], http_client: HttpClient):
        self.url = url
        self.token = token
        self.workspace = workspace
        self.http_client = http_client

    def list_screens(self) -> list:
        headers = {'Authorization': f"Bearer {self.token}"}
        if self.workspace is None:
            response = self.http_client.get(f"{self.url}/attributes/screens", headers=headers)
        else:
            params = {'versionId': self.workspace['versionId']}
            response = self.http_client.get(f"{self.url}/attributes/screens", headers=headers, params=params)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json)

        return body_json

    def update_screen(self, data_type: str, entity_type: str, categories: list) -> dict:
        headers = {'Authorization': f"Bearer {self.token}"}
        data_type = data_type.lower()
        entity_type = entity_type.lower()
        if self.workspace is None:
            response = self.http_client.put(f"{self.url}/attributes/screens/{data_type}/{entity_type}", json=categories, headers=headers)
        else:
            params = {'versionId': self.workspace['versionId']}
            response = self.http_client.put(f"{self.url}/attributes/screens/{data_type}/{entity_type}", json=categories, headers=headers, params=params)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json)
        return body_json
