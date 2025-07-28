import logging

from toolbox.api.datagalaxy_api_attributes import DataGalaxyApiAttributes, custom_attributes, find_duplicates
from toolbox.api.http_client import HttpClient


def copy_attributes(url_source: str,
                    url_target: str,
                    token_source: str,
                    token_target: str,
                    http_client: HttpClient) -> int:
    attributes_api_source = DataGalaxyApiAttributes(url=url_source, token=token_source, http_client=http_client)
    attributes_api_target = DataGalaxyApiAttributes(url=url_target, token=token_target, http_client=http_client)
    custom_source_attributes = custom_attributes(attributes_api_source)
    logging.debug(f"copy_attributes - custom_source_attributes: {custom_source_attributes}")
    logging.info(
        f'copy_attributes - {len(custom_source_attributes)} custom attributes found on source clientspace')
    if len(custom_source_attributes) == 0:
        logging.warning('copy_attributes - No custom attribute found on clientspace, aborting.')
        return 0

    custom_target_attributes = custom_attributes(attributes_api_target)
    logging.info(
        f'copy_attributes - {len(custom_target_attributes)} custom attributes found on target clientspace')

    duplicates = find_duplicates(custom_source_attributes, custom_target_attributes)
    logging.warning(f'copy_attributes - {len(duplicates)} duplicates found on target clientspace: {duplicates}')
    source_attributes_to_create = list(filter(lambda x: x['name'] not in duplicates, custom_source_attributes))

    # These attribute formats require a special behavior : we need to fetch their values and create them in a separate API call
    specific_attribute_formats = ["ValueList", "ManagedTag", "Hierarchy", "MultiValueList"]

    source_attributes_to_create_without_values = list(filter(lambda x: x['format'] not in specific_attribute_formats, source_attributes_to_create))
    source_attributes_to_create_with_values = list(filter(lambda x: x['format'] in specific_attribute_formats, source_attributes_to_create))

    # Bulk create attributes that do not have values
    logging.info('copy_attributes - Copying custom attributes (without values)')
    attributes_created_count = attributes_api_target.bulk_create(source_attributes_to_create_without_values)
    logging.info(
        f'copy_attributes - {attributes_created_count} custom attributes (without values) copied from source clientspace to target clientspace')

    logging.info('copy_attributes - Copying custom attributes (with values)')
    for attribute in source_attributes_to_create_with_values:
        format = attribute['format']
        data_type = attribute['dataType']
        attribute_key = attribute['attributeKey']
        # Fetch values from source
        values = attributes_api_source.list_values(data_type=data_type, attribute_key=attribute_key)
        # ValueList expects an array of strings
        if format == "ValueList":
            values = list(map(lambda x: x['key'], values))
        # Update default value after creation
        default_value = None
        if "defaultValue" in attribute:
            default_value = attribute["defaultValue"]
            del attribute["defaultValue"]
        # Create attribute in target
        new_attribute = attributes_api_target.create_attribute(attribute=attribute)
        # Create values in target
        if values:
            attribute_key = new_attribute['attributeKey']
            attributes_api_target.create_values(data_type=data_type, attribute_key=attribute_key, values=values)
            if default_value:
                logging.info(f"copy_attributes - Updating default value of attribute {attribute['name']}")
                attributes_api_target.update_attribute(data_type=data_type, attribute_key=attribute_key, attribute={'defaultValue': default_value})

    logging.info(
        f'copy_attributes - {len(source_attributes_to_create_with_values)} custom attributes (with values) copied from clientspace to target clientspace')

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
        help='source token',
        required=True)
    copy_attributes_parse.add_argument(
        '--token-target',
        type=str,
        help='target token',
        required=True)
