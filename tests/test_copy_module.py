from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
from toolbox.commands.copy_module import copy_module


# Mocks

def mock_list_objects_on_source_workspace(self, workspace_name):
    if workspace_name == 'workspace_source':
        return [['object1', 'object2', 'object']]
    return []


# Scenarios

def test_copy_objects_when_no_object_on_target(mocker):
    # GIVEN
    workspaces = mocker.patch.object(DataGalaxyApiWorkspace, 'list_workspaces', autospec=True)
    workspaces.return_value = ['workspace_source', 'workspace_target']
    workspace_source_mock = mocker.patch.object(DataGalaxyApiWorkspace, 'get_workspace', autospec=True)
    workspace_source_mock.return_value = {'name': 'workspace', 'defaultVersionId': 'versionId', 'isVersioningEnabled': False}
    objects_on_source_workspace_mock = mocker.patch.object(
        DataGalaxyApiModules,
        'list_objects',
        autospec=True
    )
    objects_on_source_workspace_mock.side_effect = mock_list_objects_on_source_workspace
    bulk_upsert_objects_on_target_workspace_mock = mocker.patch.object(
        DataGalaxyApiModules,
        'bulk_upsert_tree',
        autospec=True
    )
    bulk_upsert_objects_on_target_workspace_mock.return_value = 0

    # THEN
    result = copy_module(
        module="Glossary",
        url_source='url_source',
        token_source='token_source',
        url_target='url_target',
        token_target='token_target',
        workspace_source_name='workspace_source',
        version_source_name=None,
        workspace_target_name='workspace_target',
        version_target_name=None,
        tag_value=None
    )

    # ASSERT / VERIFY

    assert result == 0
    assert objects_on_source_workspace_mock.call_count == 1
    assert bulk_upsert_objects_on_target_workspace_mock.call_count == 1
