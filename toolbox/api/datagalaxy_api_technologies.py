import logging
import requests as requests


class DataGalaxyApiTechnology:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token

    def list_technologies(self) -> list:
        headers = {'Authorization': f"Bearer {self.token}"}
        response = requests.get(f"{self.url}/technologies", headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])

        logging.info(f'list_technologies - {len(body_json["technologies"])} technologies found')
        result = body_json['technologies']
        return result

    def insert_technology(self, technology) -> object:
        headers = {'Authorization': f"Bearer {self.token}"}
        response = requests.post(f"{self.url}/technologies", json=technology, headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 201:
            raise Exception(body_json['error'])
        return body_json
