from toolbox.api.datagalaxy_api import DataGalaxyApiAuthentication, Token
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
from toolbox.api.datagalaxy_api_glossary import DataGalaxyApiGlossary
from toolbox.commands.delete_glossary import delete_glossary


# Mock
def mock_list_glossary_properties(self, data_type):
    if self.url == 'url':
        return [
            {
                'id': '1',
                'name': 'Object',
                'description': 'An object in the glossary'
            }
        ]

    return []


# Scenarios
def test_delete_glossary(mocker):
    # GIVEN
    client_space_mock = mocker.patch.object(Token, 'get_client_space_id', autospec=True)
    client_space_mock.return_value = 'cid'
    api_authenticate_mock = mocker.patch.object(DataGalaxyApiAuthentication, 'authenticate', autospec=True)
    api_authenticate_mock.return_value = 'token'
    workspaces = mocker.patch.object(DataGalaxyApiWorkspace, 'list_workspaces', autospec=True)
    workspaces.return_value = ['workspace']
    workspace_mock = mocker.patch.object(DataGalaxyApiWorkspace, 'get_workspace', autospec=True)
    workspace_mock.return_value = 'workspace'
    glossary_list_mock = mocker.patch.object(DataGalaxyApiGlossary, 'list_properties', autospec=True)
    glossary_list_mock.side_effect = mock_list_glossary_properties
    delete_glossary_mock = mocker.patch.object(DataGalaxyApiGlossary, 'delete_objects', autospec=True)
    delete_glossary_mock.return_value = True

    # THEN
    result = delete_glossary(url='url', token='token', workspace_name="workspace")

    # ASSERT / VERIFY
    assert result is True
