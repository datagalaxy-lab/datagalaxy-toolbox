from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.commands.delete_module import delete_module


# Mock
mock_list_objects = [[
                        {
                            'id': '1',
                            'name': 'Object',
                            'path': "\\\\Object",
                            'description': 'Just a simple object'
                        }
                    ]]


# Scenarios
def test_delete_module(mocker):
    # GIVEN
    workspaces = mocker.patch.object(DataGalaxyApiWorkspace, 'list_workspaces', autospec=True)
    workspaces.return_value = ['workspace']
    workspace_mock = mocker.patch.object(DataGalaxyApiWorkspace, 'get_workspace', autospec=True)
    workspace_mock.return_value = {'name': 'workspace', 'defaultVersionId': 'versionId', 'isVersioningEnabled': False}
    objects_list_mock = mocker.patch.object(DataGalaxyApiModules, 'list_objects', autospec=True)
    objects_list_mock.return_value = mock_list_objects
    delete_objects_mock = mocker.patch.object(DataGalaxyApiModules, 'delete_objects', autospec=True)
    delete_objects_mock.return_value = True

    # THEN
    result = delete_module(module="Glossary", url='url', token='token', workspace_name="workspace", version_name=None)

    # ASSERT / VERIFY
    assert result == 0
