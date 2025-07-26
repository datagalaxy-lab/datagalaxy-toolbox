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

    def update_screen(self, screen) -> object:
        headers = {'Authorization': f"Bearer {self.token}"}
        dataType = screen['dataType'].lower()
        type = screen['type'].lower()
        categories = screen['categories']
        if self.workspace is None:
            response = self.http_client.put(f"{self.url}/attributes/screens/{dataType}/{type}", json=categories, headers=headers)
        else:
            params = {'versionId': self.workspace['versionId']}
            response = self.http_client.put(f"{self.url}/attributes/screens/{dataType}/{type}", json=categories, headers=headers, params=params)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json)
        return body_json
