from toolbox.api.datagalaxy_api import DataGalaxyApiAuthentication, Token
from toolbox.api.datagalaxy_api_attributes import AttributeDataType, DataGalaxyApiAttributes
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
    client_space_mock = mocker.patch.object(Token, 'get_client_space_id', autospec=True)
    client_space_mock.return_value = 'cid'
    api_authenticate_mock = mocker.patch.object(DataGalaxyApiAuthentication, 'authenticate', autospec=True)
    api_authenticate_mock.return_value = 'token'
    attributes_list_mock = mocker.patch.object(DataGalaxyApiAttributes, 'list', autospec=True)
    attributes_list_mock.side_effect = mock_list_attributes
    delete_attributes_mock = mocker.patch.object(DataGalaxyApiAttributes, 'delete_attribute', autospec=True)
    delete_attributes_mock.return_value = True

    # THEN
    result = delete_attributes(url='url',
                               integration_token_value='token')

    # ASSERT / VERIFY
    assert result is True
