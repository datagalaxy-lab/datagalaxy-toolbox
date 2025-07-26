from toolbox.api.datagalaxy_api_attributes import AttributeDataType, DataGalaxyApiAttributes
from toolbox.api.http_client import HttpClient
from toolbox.commands.delete_attributes import delete_attributes


# Mock
def mock_list_attributes(self, data_type):
    if self.url == 'url_source' and data_type == AttributeDataType.COMMON:
        return [
            {
                'name': 'Custom Property',
                'format': 'MultiValueList',
                'description': 'New Custom property'
            }
        ]

    return []


# Scenarios
def test_delete_attributes(mocker):
    # GIVEN
    attributes_list_mock = mocker.patch.object(DataGalaxyApiAttributes, 'list', autospec=True)
    attributes_list_mock.side_effect = mock_list_attributes
    delete_attributes_mock = mocker.patch.object(DataGalaxyApiAttributes, 'delete_attribute', autospec=True)
    delete_attributes_mock.return_value = True

    # THEN
    http_client = HttpClient(verify_ssl=True)
    result = delete_attributes(url='url', token='token', http_client=http_client)

    # ASSERT / VERIFY
    assert result is True
