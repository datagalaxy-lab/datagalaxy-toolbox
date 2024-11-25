from toolbox.api.datagalaxy_api_attributes import AttributeDataType, DataGalaxyApiAttributes
from toolbox.commands.copy_attributes import copy_attributes
from unittest.mock import ANY


# Mocks

def list_mock_return_many_attr(self, data_type):
    if self.url == 'url_source' and data_type == AttributeDataType.COMMON:
        return [
            {
                'name': 'Custom Property',
                'attributeKey': 'CP',
                'format': 'Text',
                'description': 'New Custom property'
            },
            {
                'name': 'Custom Property 2',
                'attributeKey': 'CP2',
                'format': 'Text',
                'description': 'New Custom property 2'
            },
            {
                'name': 'Custom Property 3',
                'attributeKey': 'CP3',
                'format': 'Text',
                'description': 'New Custom property 3'
            }
        ]

    return []


def list_mock_return_one_common_attr(self, data_type):
    if self.url == 'url_source' and data_type == AttributeDataType.COMMON:
        return [
            {
                'name': 'Custom Property',
                'format': 'Text',
                'description': 'New Custom property'
            }
        ]

    return []


def list_mock_when_duplicates(self, data_type):
    return [
        {
            'name': 'Duplicate',
            'format': 'Text',
            'description': 'New Custom property'
        }
    ]


# Scenarios

def test_copy_attributes_when_only_one_source_attr_and_duplicates_on_target(mocker):
    """
    Scenario 1. error
    :param mocker:
    :return: raise Exception
    """
    attributes_list_mock = mocker.patch.object(DataGalaxyApiAttributes, 'list', autospec=True)
    attributes_list_mock.side_effect = list_mock_when_duplicates
    attributes_bulk_create_mock = mocker.patch.object(DataGalaxyApiAttributes, 'bulk_create', autospec=True)
    attributes_bulk_create_mock.return_value = None

    # ASSERT / VERIFY
    result = copy_attributes(
            url_source='url_source',
            url_target='url_target',
            token_source='token_source',
            token_target='token_target'
        )
    assert attributes_list_mock.call_count == 16
    assert attributes_bulk_create_mock.call_count == 1
    assert result is None


def test_copy_attributes_when_no_source_attr(mocker):
    """
    Scenario 2
    :param mocker:
    :return: 0
    """
    # GIVEN
    attributes_list_mock = mocker.patch.object(DataGalaxyApiAttributes, 'list', autospec=True)
    attributes_list_mock.return_value = []
    attributes_bulk_create_mock = mocker.patch.object(DataGalaxyApiAttributes, 'bulk_create', autospec=True)
    attributes_bulk_create_mock.return_value = None

    # THEN
    result = copy_attributes(
        url_source='url_source',
        url_target='url_target',
        token_source='token_source',
        token_target='token_target'
    )
    # ASSERT / VERIFY
    assert attributes_list_mock.call_count == 8
    assert attributes_bulk_create_mock.call_count == 0
    assert result == 0


def test_copy_attributes_when_many_source_attrs(mocker):
    """
   Scenario 3. error
   :param mocker:
   :return: raise Exception
   """
    # GIVEN
    attributes_list_mock = mocker.patch.object(DataGalaxyApiAttributes, 'list', autospec=True)
    attributes_list_mock.side_effect = list_mock_return_many_attr
    attributes_bulk_create_mock = mocker.patch.object(DataGalaxyApiAttributes, 'bulk_create', autospec=True)
    attributes_bulk_create_mock.return_value = 3

    # THEN
    result = copy_attributes(
        url_source='url_source',
        url_target='url_target',
        token_source='token_source',
        token_target='token_target'
    )
    # ASSERT / VERIFY
    assert attributes_list_mock.call_count == 16
    assert attributes_bulk_create_mock.call_count == 1
    assert attributes_bulk_create_mock.call_args.args == (ANY, [
        {
            'name': 'Custom Property',
            'attributeKey': 'CP',
            'format': 'Text',
            'description': 'New Custom property',
            'dataType': 'Common'
        },
        {
            'name': 'Custom Property 2',
            'attributeKey': 'CP2',
            'format': 'Text',
            'description': 'New Custom property 2',
            'dataType': 'Common'
        },
        {
            'name': 'Custom Property 3',
            'attributeKey': 'CP3',
            'format': 'Text',
            'description': 'New Custom property 3',
            'dataType': 'Common'
        }
    ])

    assert result == 3


def test_copy_attributes_when_only_one_source_attr_and_empty_target(mocker):
    """
   Scenario 4. error
   :param mocker:
   :return: raise Exception
   """
    # GIVEN
    attributes_list_mock = mocker.patch.object(DataGalaxyApiAttributes, 'list', autospec=True)
    attributes_list_mock.side_effect = list_mock_return_one_common_attr
    attributes_bulk_create_mock = mocker.patch.object(DataGalaxyApiAttributes, 'bulk_create', autospec=True)
    attributes_bulk_create_mock.return_value = 1

    # THEN
    result = copy_attributes(
        url_source='url_source',
        url_target='url_target',
        token_source='token_source',
        token_target='token_target'
    )

    # ASSERT / VERIFY
    assert attributes_list_mock.call_count == 16
    assert attributes_bulk_create_mock.call_count == 1
    assert attributes_bulk_create_mock.call_args.args == (ANY, [
        {
            'name': 'Custom Property',
            'format': 'Text',
            'description': 'New Custom property',
            'dataType': 'Common'
        }
    ])

    assert result == 1
