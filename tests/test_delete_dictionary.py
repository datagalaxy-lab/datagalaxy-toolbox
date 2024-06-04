from toolbox.api.datagalaxy_api import DataGalaxyApiAuthentication, Token
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
from toolbox.api.datagalaxy_api_dictionary import DataGalaxyApiDictionary
from toolbox.commands.delete_dictionary import delete_dictionary


# Mock
def mock_list_sources(self, data_type):
    if self.url == 'url':
        return [
            {
                'id': '1',
                'name': 'Object',
                'description': 'An object in the dictionary'
            }
        ]

    return []


# Scenarios
def test_delete_dictionary(mocker):
    # GIVEN
    client_space_mock = mocker.patch.object(Token, 'get_client_space_id', autospec=True)
    client_space_mock.return_value = 'cid'
    api_authenticate_mock = mocker.patch.object(DataGalaxyApiAuthentication, 'authenticate', autospec=True)
    api_authenticate_mock.return_value = 'token'
    workspaces = mocker.patch.object(DataGalaxyApiWorkspace, 'list_workspaces', autospec=True)
    workspaces.return_value = ['workspace']
    workspace_mock = mocker.patch.object(DataGalaxyApiWorkspace, 'get_workspace', autospec=True)
    workspace_mock.return_value = {'isVersioningEnabled': False}
    dictionary_list_mock = mocker.patch.object(DataGalaxyApiDictionary, 'list_sources', autospec=True)
    dictionary_list_mock.side_effect = mock_list_sources
    delete_dictionary_mock = mocker.patch.object(DataGalaxyApiDictionary, 'delete_sources', autospec=True)
    delete_dictionary_mock.return_value = True

    # THEN
    result = delete_dictionary(url='url', token='token', workspace_name="workspace")

    # ASSERT / VERIFY
    assert result is True
