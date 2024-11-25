import requests as requests


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

        raise Exception(f'Workspace {name} does not exist, workspaces found: {workspaces}')
