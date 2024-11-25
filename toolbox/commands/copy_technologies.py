import logging

from toolbox.api.datagalaxy_api_technologies import DataGalaxyApiTechnology


def copy_technologies(url_source: str,
                      url_target: str,
                      token_source: str,
                      token_target: str) -> int:

    technologies_api_source = DataGalaxyApiTechnology(url=url_source, token=token_source)
    technologies_api_target = DataGalaxyApiTechnology(url=url_target, token=token_target)

    source_technologies = technologies_api_source.list_technologies()
    target_technologies = technologies_api_target.list_technologies()

    if len(source_technologies) == 0:
        raise Exception('no technology found on source clientspace')

    # custom technologies have a "creationUserId" that is not set on the default value
    source_custom_technologies = list(filter(lambda technology: technology['creationUserId'] != "00000000-0000-0000-0000-000000000000", source_technologies))

    if len(source_custom_technologies) == 0:
        logging.info('copy_technologies - No custom technology found on source client_space, aborting.')
        return 0

    logging.info(f'copy_technologies - {len(source_custom_technologies)} custom technologies found on source client_space')

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

    logging.info(f'copy_technologies - {count_created_technologies} technologies were created on target client_space')
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
        help='source token',
        required=True)
    copy_technologies_parse.add_argument(
        '--token-target',
        type=str,
        help='target token',
        required=True)
