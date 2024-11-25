from toolbox.api.datagalaxy_api_dictionary import DataGalaxyApiDictionary
from toolbox.commands.copy_dictionary import copy_dictionary
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
import pytest as pytest


# Mocks

def mock_list_sources_on_source_workspace(self, workspace_name):
    if workspace_name == 'workspace_source':
        return ['source1', 'source2', 'source3']
    return []


# Scenarios

def test_copy_sources_when_workspace_source_does_not_exist(mocker):
    # GIVEN
    workspaces = mocker.patch.object(DataGalaxyApiWorkspace, 'list_workspaces', autospec=True)
    workspaces.return_value = ['workspace_source']
    workspace_source_mock = mocker.patch.object(DataGalaxyApiWorkspace, 'get_workspace', autospec=True)
    workspace_source_mock.return_value = None
    sources_on_source_workspace_mock = mocker.patch.object(
        DataGalaxyApiDictionary,
        'list_sources',
        autospec=True
    )
    sources_on_source_workspace_mock.side_effect = mock_list_sources_on_source_workspace

    # ASSERT / VERIFY
    with pytest.raises(Exception, match='workspace workspace_source does not exist'):
        copy_dictionary(
            url_source='url_source',
            token_source='token_source',
            url_target='url_target',
            token_target='token_target',
            workspace_source_name='workspace_source',
            workspace_target_name='workspace_target',
            tag_value=None
        )
