import logging

from toolbox.api.datagalaxy_api_attributes import DataGalaxyApiAttributes, custom_attributes
from toolbox.api.http_client import HttpClient


def delete_attributes(url: str, token: str, http_client: HttpClient) -> bool:
    attributes_api_target = DataGalaxyApiAttributes(url=url, token=token, http_client=http_client)
    custom_target_attributes = custom_attributes(attributes_api_target)
    logging.info(
        f'delete_attributes - {len(custom_target_attributes)} custom attributes found on clientspace')
    attributes_api_target.delete_all_attributes(custom_target_attributes)
    logging.info(
        f'delete_attributes - {len(custom_target_attributes)} custom attributes deleted on clientspace')
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
