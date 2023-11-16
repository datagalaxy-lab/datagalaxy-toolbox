import logging

from toolbox.api.datagalaxy_api import get_access_token, Token
from toolbox.api.datagalaxy_api_technologies import DataGalaxyApiTechnology


def copy_technologies(url_source: str,
                      url_target: str,
                      integration_token_source_value: str,
                      integration_token_target_value: str) -> int:
    integration_token_source = Token(integration_token_source_value)
    integration_token_target = Token(integration_token_target_value)

    source_client_space_id = integration_token_source.get_client_space_id()

    access_token_source = get_access_token(url_source, integration_token_source)
    access_token_target = get_access_token(url_target, integration_token_target)

    technologies_api_source = DataGalaxyApiTechnology(url=url_source, access_token=access_token_source)
    technologies_api_target = DataGalaxyApiTechnology(url=url_target, access_token=access_token_target)

    source_technologies = technologies_api_source.list_technologies()
    target_technologies = technologies_api_target.list_technologies()

    if len(source_technologies) == 0:
        raise Exception('no technology found on source clientspace')

    # custom technologies have a "creationUserId" that is not set on the default value
    source_custom_technologies = list(filter(lambda technology: technology['creationUserId'] != "00000000-0000-0000-0000-000000000000", source_technologies))

    if len(source_custom_technologies) == 0:
        logging.info(f'copy_technologies - No custom technology found on source client_space: {source_client_space_id}, aborting.')
        return 0

    logging.info(f'copy_technologies - {len(source_custom_technologies)} custom technologies found on client_space: {source_client_space_id}')

    target_technology_codes = list(map(lambda t: t['technologyCode'], target_technologies))

    count_created_technologies = 0
    for source_custom in source_custom_technologies:
        # We check that the custom technology code does not already exists on the target clientspace
        if source_custom['technologyCode'] in target_technology_codes:
            logging.info(f'copy_technologies - {source_custom["technologyCode"]} already exists in target')
            continue

        # That is not the case, so we create the technology in the target clientspace
        logging.info(f'copy_technologies - {source_custom["technologyCode"]} does not exists in target')
        technologies_api_target.insert_technology(source_custom)
        count_created_technologies += 1

    logging.info(f'copy_technologies - {count_created_technologies} technologies were created on target client_space: {source_client_space_id}')
    return count_created_technologies


def copy_technologies_parse(subparsers):
    # create the parser for the "copy-technologies" command
    copy_technologies_parse = subparsers.add_parser('copy-technologies', help='copy-technologies help')
    copy_technologies_parse.add_argument(
        '--url-source',
        type=str,
        help='url source',
        required=True)
    copy_technologies_parse.add_argument(
        '--url-target',
        type=str,
        help='url target',
        required=True)
    copy_technologies_parse.add_argument(
        '--token-source',
        type=str,
        help='integration source token',
        required=True)
    copy_technologies_parse.add_argument(
        '--token-target',
        type=str,
        help='integration target token',
        required=True)
