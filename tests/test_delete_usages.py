from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
from toolbox.api.datagalaxy_api_usages import DataGalaxyApiUsages
from toolbox.commands.delete_usages import delete_usages


# Mock
def mock_list_usages(self, data_type):
    if self.url == 'url':
        return [
            {
                'id': '1',
                'name': 'Object',
                'description': 'An object in the usages'
            }
        ]

    return []


# Scenarios
def test_delete_usages(mocker):
    # GIVEN
    workspaces = mocker.patch.object(DataGalaxyApiWorkspace, 'list_workspaces', autospec=True)
    workspaces.return_value = ['workspace']
    workspace_mock = mocker.patch.object(DataGalaxyApiWorkspace, 'get_workspace', autospec=True)
    workspace_mock.return_value = 'workspace'
    usages_list_mock = mocker.patch.object(DataGalaxyApiUsages, 'list_usages', autospec=True)
    usages_list_mock.side_effect = mock_list_usages
    delete_usages_mock = mocker.patch.object(DataGalaxyApiUsages, 'delete_objects', autospec=True)
    delete_usages_mock.return_value = True

    # THEN
    result = delete_usages(url='url', token='token', workspace_name="workspace")

    # ASSERT / VERIFY
    assert result is True
