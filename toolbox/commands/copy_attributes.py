import logging

from toolbox.api.datagalaxy_api import get_access_token, Token
from toolbox.api.datagalaxy_api_attributes import DataGalaxyApiAttributes, custom_attributes, find_duplicates


def copy_attributes(url_source: str,
                    url_target: str,
                    integration_token_source_value: str,
                    integration_token_target_value: str) -> int:
    integration_token_source = Token(integration_token_source_value)
    integration_token_target = Token(integration_token_target_value)

    source_client_space_id = integration_token_source.get_client_space_id()
    target_client_space_id = integration_token_target.get_client_space_id()

    access_token_source = get_access_token(url_source, integration_token_source)
    access_token_target = get_access_token(url_target, integration_token_target)
    attributes_api_source = DataGalaxyApiAttributes(url=url_source, access_token=access_token_source)
    attributes_api_target = DataGalaxyApiAttributes(url=url_target, access_token=access_token_target)
    custom_source_attributes = custom_attributes(attributes_api_source)
    logging.debug(f"copy_attributes - custom_source_attributes: {custom_source_attributes}")
    logging.info(
        f'copy_attributes - {len(custom_source_attributes)} custom attributes found on client_space: {source_client_space_id}')
    if len(custom_source_attributes) == 0:
        logging.warning(f'copy_attributes - no attribute found on client_space: {source_client_space_id}, aborting.')
        return 0

    custom_target_attributes = custom_attributes(attributes_api_target)
    logging.info(
        f'copy_attributes - {len(custom_target_attributes)} custom attributes found on client_space: {target_client_space_id}')

    duplicates = find_duplicates(custom_source_attributes, custom_target_attributes)
    logging.warning(f'copy_attributes - {len(duplicates)} duplicates found on client_space: {target_client_space_id}: {duplicates}')
    source_attributes_to_create = list(filter(lambda x: x['name'] not in duplicates, custom_source_attributes))
    attributes_created_count = attributes_api_target.bulk_create(source_attributes_to_create)
    logging.info(
        f'copy_attributes - {attributes_created_count} custom attributes copied from client_space: '
        f'{source_client_space_id} to client_space: {target_client_space_id}')
    return attributes_created_count


def copy_attributes_parse(subparsers):
    # create the parser for the "copy-attributes" command
    copy_attributes_parse = subparsers.add_parser('copy-attributes', help='copy-attributes help')
    copy_attributes_parse.add_argument(
        '--url-source',
        type=str,
        help='url source',
        required=True)
    copy_attributes_parse.add_argument(
        '--url-target',
        type=str,
        help='url target',
        required=True)
    copy_attributes_parse.add_argument(
        '--token-source',
        type=str,
        help='integration source token',
        required=True)
    copy_attributes_parse.add_argument(
        '--token-target',
        type=str,
        help='integration target token',
        required=True)
