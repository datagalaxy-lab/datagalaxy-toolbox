import requests as requests
import logging


class DataGalaxyApiWorkspace:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token

    def list_workspaces(self):
        headers = {'Authorization': f"Bearer {self.token}"}
        response = requests.get(f"{self.url}/workspaces", headers=headers)
        code = response.status_code
        body_json = response.json()
        if code == 200:
            workspaces = []
            for workspace in body_json["projects"]:
                workspaces.append(workspace)
            return workspaces

        if 400 <= code < 500:
            raise Exception(body_json['error'])

        raise Exception(f'Unexpected error, code: {code}')

    def get_workspace(self, name: str) -> dict:
        workspaces = []
        for workspace in self.list_workspaces():
            workspaces.append(workspace['name'])
            if workspace['name'] == name:
                return workspace

        logging.error(f'get_workspace - Workspace {name} does not exist, workspaces found: {workspaces}')
        return None

    def list_versions(self, id_workspace: str) -> dict:
        headers = {'Authorization': f"Bearer {self.token}", 'limit': '5000'}
        response = requests.get(f"{self.url}/workspaces/{id_workspace}/versions", headers=headers)
        code = response.status_code
        body_json = response.json()
        if code == 200:
            versions = []
            for version in body_json["results"]:
                versions.append(version)
            return versions

        if 400 <= code < 500:
            raise Exception(body_json['error'])

        raise Exception(f'Unexpected error, code: {code}')

    def get_version(self, id_workspace: str, name: str) -> dict:
        versions = []
        for version in self.list_versions(id_workspace):
            versions.append(version['versionName'])
            if version['versionName'] == name:
                return version

        logging.error(f'get_version - Version {name} does not exist, versions found: {versions}')
        return None
