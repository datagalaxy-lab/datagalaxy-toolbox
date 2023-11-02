from toolbox.api.datagalaxy_api_dataprocessings import DataGalaxyApiDataprocessings
from toolbox.commands.copy_dataprocessings import copy_dataprocessings
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace

from toolbox.api.datagalaxy_api import DataGalaxyApiAuthentication, Token
import pytest as pytest


# Mocks

def mock_list_dataprocessings_on_source_workspace(self, workspace_name):
    if workspace_name == 'workspace_source':
        return ['dataprocessing1', 'dataprocessing2', 'dataprocessing3']
    return []


# Scenarios

def test_copy_dataprocessings_when_workspace_source_does_not_exist(mocker):
    # GIVEN
    client_space_mock = mocker.patch.object(Token, 'get_client_space_id', autospec=True)
    client_space_mock.return_value = 'cid'
    api_authenticate_mock = mocker.patch.object(DataGalaxyApiAuthentication, 'authenticate', autospec=True)
    api_authenticate_mock.return_value = 'token'
    workspaces = mocker.patch.object(DataGalaxyApiWorkspace, 'list_workspaces', autospec=True)
    workspaces.return_value = ['workspace_source']
    workspace_source_mock = mocker.patch.object(DataGalaxyApiWorkspace, 'get_workspace', autospec=True)
    workspace_source_mock.return_value = None
    dataprocessings_on_source_workspace_mock = mocker.patch.object(
        DataGalaxyApiDataprocessings,
        'list_dataprocessings',
        autospec=True
    )
    dataprocessings_on_source_workspace_mock.side_effect = mock_list_dataprocessings_on_source_workspace

    # ASSERT / VERIFY
    with pytest.raises(Exception, match='workspace workspace_source does not exist'):
        copy_dataprocessings(
            url_source='url_source',
            token_source='token_source',
            url_target='url_target',
            token_target='token_target',
            workspace_source_name='workspace_source',
            workspace_target_name='workspace_target'
        )
