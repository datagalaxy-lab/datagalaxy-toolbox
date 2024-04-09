import requests as requests
from typing import Optional


class DataGalaxyApiScreen:
    def __init__(self, url: str, access_token: str, workspace: Optional[dict]):
        self.url = url
        self.access_token = access_token
        self.workspace = workspace

    def list_screens(self) -> list:
        headers = {'Authorization': f"Bearer {self.access_token}"}
        if self.workspace is None:
            response = requests.get(f"{self.url}/attributes/screens", headers=headers)
        else:
            params = {'versionId': self.workspace['defaultVersionId']}
            response = requests.get(f"{self.url}/attributes/screens", headers=headers, params=params)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json)

        return body_json

    def update_screen(self, screen) -> object:
        headers = {'Authorization': f"Bearer {self.access_token}"}
        dataType = screen['dataType'].lower()
        type = screen['type'].lower()
        categories = screen['categories']
        if self.workspace is None:
            response = requests.put(f"{self.url}/attributes/screens/{dataType}/{type}", json=categories, headers=headers)
        else:
            params = {'versionId': self.workspace['defaultVersionId']}
            response = requests.put(f"{self.url}/attributes/screens/{dataType}/{type}", json=categories, headers=headers, params=params)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json)
        return body_json
