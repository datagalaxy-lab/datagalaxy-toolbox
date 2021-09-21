import logging

from toolbox.api.datagalaxy_api import get_access_token, Token
from toolbox.api.datagalaxy_api_attributes import DataGalaxyApiAttributes, custom_attributes


def delete_attributes(url: str, integration_token_value: str) -> bool:
    integration_token = Token(integration_token_value)
    client_space_id = integration_token.get_client_space_id()

    access_token_target = get_access_token(url, integration_token)
    attributes_api_target = DataGalaxyApiAttributes(url=url, access_token=access_token_target)
    custom_target_attributes = custom_attributes(attributes_api_target)
    logging.info(
        f'delete_attributes - {len(custom_target_attributes)} custom attributes found on client_space: {client_space_id}')
    attributes_api_target.delete_all_attributes(custom_target_attributes)
    logging.info(
        f'delete_attributes - {len(custom_target_attributes)} custom attributes deleted on client_space: {client_space_id}')
    return True


def delete_attributes_parse(subparsers):
    # create the parser for the "delete-attributes" command
    delete_attributes_parse = subparsers.add_parser('delete-attributes', help='delete-attributes help')
    delete_attributes_parse.add_argument('--url',
                                         type=str,
                                         help='url source',
                                         required=True)

    delete_attributes_parse.add_argument('--token',
                                         type=str,
                                         help='token',
                                         required=True)
