from dataclasses import dataclass

import jwt
import requests
import logging

logging.basicConfig(level=logging.INFO,
                    format='{asctime} {levelname} {message}',
                    style='{'
                    )


class Token:
    def __init__(self, value):
        self.value = value

    def get_client_space_id(self) -> str:
        decode_token = jwt.decode(
            self.value,
            options={"verify_signature": False},
            algorithms=["HS256"]
        )
        client_space_id = decode_token["cid"]
        return client_space_id


@dataclass
class DataGalaxyApi:
    url: str
    token: Token


class DataGalaxyApiAuthentication:
    def __init__(self, datagalaxy_api: DataGalaxyApi):
        self.datagalaxy_api = datagalaxy_api

    def authenticate(self) -> str:
        """
        Generate an access token from the DataGalaxy API.

        Documentation: https://apici.datagalaxy.com/v2/documentation/beta#operation/Generate
        :return: an access token
        """
        headers = {"Authorization": f"Bearer {self.datagalaxy_api.token.value}"}
        request = requests.get(f"{self.datagalaxy_api.url}/credentials", headers=headers)
        body_json = request.json()
        code = request.status_code
        if code == 200:
            return body_json['accessToken']
        elif 400 <= code < 500:
            raise Exception(body_json['error'])
        else:
            raise Exception(f'Unexpected error, code: {code}')


def get_access_token(url: str, integration_token: Token):
    dev_uat_env = DataGalaxyApi(url, integration_token)
    auth_api = DataGalaxyApiAuthentication(dev_uat_env)
    access_token = auth_api.authenticate()
    client_space_id = integration_token.get_client_space_id()
    logging.info(f'get_access_token - Authenticating [url: {url} , client_space: {client_space_id}]')
    return access_token
