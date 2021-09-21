import logging
from enum import Enum

import requests as requests


class AttributeDataType(Enum):
    """
    ...
    """
    COMMON = 'Common'
    PROPERTY = 'Property'
    SOURCE = 'Source'
    CONTAINER = 'Container'
    STRUCTURE = 'Structure'
    FIELD = 'Field'
    DATA_PROCESSING = 'DataProcessing'
    USAGE = 'Usage'


class DataGalaxyApiAttributes:
    def __init__(self, url: str, access_token: str):
        self.url = url
        self.access_token = access_token

    def list(self, data_type: AttributeDataType, only_custom=True) -> list:
        params = {'dataType': data_type.value.lower()}
        headers = {'Authorization': f"Bearer {self.access_token}"}
        request = requests.get(f"{self.url}/attributes", params=params, headers=headers)
        code = request.status_code
        body_json = request.json()

        if code == 200:
            if only_custom is False:
                return body_json

            return list(filter(lambda attr: attr['isCustom'] is True, body_json))

        if 400 <= code < 500:
            raise Exception(body_json['error'])

        raise Exception(f'Unexpected error, code: {code}')

    def bulk_create(self, attributes: list) -> int:
        # attributes in "ValueList", "ManagedTag", "Hierarchy", "MultiValueList" formats are ignored because
        # the values are not yet copied and the api returns an error 400 with the message:
        # "Object reference not set to an instance of an object"

        invalid_attribute_formats = ["ValueList", "ManagedTag", "Hierarchy", "MultiValueList"]
        valid_attributes = [attr for attr in attributes if attr['format'] not in invalid_attribute_formats]
        invalid_attributes = [attr for attr in attributes if attr['format'] in invalid_attribute_formats]
        invalid_attrs_name_format = list(map(lambda a: f"{a['name']}/{a['format']}", invalid_attributes))
        logging.warning(
            f"bulk_create - {len(invalid_attributes)} ignored attributs: {invalid_attrs_name_format} using "
            f"an unsupported formats: {invalid_attribute_formats}")

        bulk_attributes = list(map(to_bulk_item_attribute, valid_attributes))
        bulks = [bulk_attributes[i:i + 50] for i in range(0, len(bulk_attributes), 50)]

        for bulk in bulks:
            headers = {'Authorization': f"Bearer {self.access_token}"}
            logging.debug(f"bulk_create - bulk_create(bulk: {bulk})")
            request = requests.post(f"{self.url}/attributes/bulk", json=bulk, headers=headers)

            code = request.status_code
            body_json = request.json()

            if 200 <= code < 300:
                continue

            if 400 <= code < 500:
                logging.info(f"bulk_create - Something went wrong: {body_json}")
                raise Exception(body_json['error'])

            raise Exception(f'Unexpected error, code: {code}')

        return len(valid_attributes)

    def delete_attribute(self, data_type: AttributeDataType, attribute_key: str) -> bool:
        logging.debug(f"delete_attribute- delete_attribute(data_type: {data_type}, attribute_key: {attribute_key})")
        headers = {'Authorization': f"Bearer {self.access_token}"}
        request = requests.delete(f"{self.url}/attributes/{data_type}/{attribute_key}", headers=headers)
        code = request.status_code
        body_json = request.json()
        logging.debug(f"delete_attribute - delete_attribute.response(body_json: {body_json}, code: {code})")
        if 200 <= code < 300:
            return True

        if 400 <= code < 500:
            raise Exception(body_json['error'])

        raise Exception(f'Unexpected error, code: {code}')

    def delete_all_attributes(self, attributes: list) -> bool:
        for attribute in attributes:
            data_type = attribute['dataType'].lower()
            attribute_key = attribute['attributeKey']
            self.delete_attribute(data_type=data_type, attribute_key=attribute_key)

        return True


EXPECTED_BULK_ATTRIBUTE_FIELDS = [
    'name', 'format', 'description', 'defaultValue', 'timeSeriesFrequency', 'timeSeriesColorRule', 'dataType'
]


def to_bulk_item_attribute(attribute):
    for key in ['name', 'format']:
        if key not in list(attribute.keys()):
            raise Exception(f'{key} is missing on {attribute} attribute')
        else:
            continue

    for key in list(attribute.keys()):
        if key not in EXPECTED_BULK_ATTRIBUTE_FIELDS:
            del attribute[key]

    return attribute


def with_data_type(attribute, data_type):
    attribute['dataType'] = data_type.value
    return attribute


def _get_name(attr: dict) -> str:
    return attr['name']


def find_duplicates(attrs: list, other_attrs: list) -> set:
    attrs_set = set(map(_get_name, attrs))
    other_attrs_set = set(map(_get_name, other_attrs))
    return attrs_set.intersection(other_attrs_set)


def custom_attributes(attributes_api: DataGalaxyApiAttributes):
    attributes_by_data_type = []

    # get common attributes
    common_attributes = attributes_api.list(AttributeDataType.COMMON)

    # get attributes for all other data type (i.e., all except COMMON)
    for data_type in list(filter(lambda it: it != AttributeDataType.COMMON, list(AttributeDataType))):
        attributes = attributes_api.list(data_type)
        # remove common attributes
        attributes_without_common = [item for item in attributes if item not in common_attributes]
        logging.debug(f"custom_attributes - Found attributes: {attributes_without_common} for dataType: {data_type}")
        attributes_by_data_type.append(
            list(map(lambda _attr: with_data_type(_attr, data_type), attributes_without_common))
        )

    return [item for sublist in attributes_by_data_type for item in sublist] + list(
        map(lambda _attr: with_data_type(_attr, AttributeDataType.COMMON), common_attributes))
