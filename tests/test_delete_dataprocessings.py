from toolbox.api.datagalaxy_api import DataGalaxyApiAuthentication, Token
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
from toolbox.api.datagalaxy_api_dataprocessings import DataGalaxyApiDataprocessings
from toolbox.commands.delete_dataprocessings import delete_dataprocessings


# Mock
def mock_list_dataprocessings(self, data_type):
    if self.url == 'url':
        return [
            {
                'id': '1',
                'name': 'Object',
                'description': 'An object in the dataprocessings'
            }
        ]

    return []


# Scenarios
def test_delete_dataprocessings(mocker):
    # GIVEN
    client_space_mock = mocker.patch.object(Token, 'get_client_space_id', autospec=True)
    client_space_mock.return_value = 'cid'
    api_authenticate_mock = mocker.patch.object(DataGalaxyApiAuthentication, 'authenticate', autospec=True)
    api_authenticate_mock.return_value = 'token'
    workspaces = mocker.patch.object(DataGalaxyApiWorkspace, 'list_workspaces', autospec=True)
    workspaces.return_value = ['workspace']
    workspace_mock = mocker.patch.object(DataGalaxyApiWorkspace, 'get_workspace', autospec=True)
    workspace_mock.return_value = {'isVersioningEnabled': False}
    dataprocessings_list_mock = mocker.patch.object(DataGalaxyApiDataprocessings, 'list_dataprocessings', autospec=True)
    dataprocessings_list_mock.side_effect = mock_list_dataprocessings
    delete_dataprocessings_mock = mocker.patch.object(DataGalaxyApiDataprocessings, 'delete_objects', autospec=True)
    delete_dataprocessings_mock.return_value = True

    # THEN
    result = delete_dataprocessings(url='url', token='token', workspace_name="workspace")

    # ASSERT / VERIFY
    assert result is True
