import logging
import requests as requests
from .http_client import HttpClient


class DataGalaxyApiTechnology:
    def __init__(self, url: str, token: str, http_client: HttpClient):
        self.url = url
        self.token = token
        self.http_client = http_client

    def list_technologies(self) -> list:
        headers = {'Authorization': f"Bearer {self.token}"}
        response = self.http_client.get(f"{self.url}/technologies", headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 200:
            raise Exception(body_json['error'])

        logging.info(f'list_technologies - {len(body_json["technologies"])} technologies found')
        result = body_json['technologies']
        return result

    def insert_technology(self, technology) -> object:
        headers = {'Authorization': f"Bearer {self.token}"}
        response = self.http_client.post(f"{self.url}/technologies", json=technology, headers=headers)
        code = response.status_code
        body_json = response.json()
        if code != 201:
            raise Exception(body_json['error'])
        return body_json
