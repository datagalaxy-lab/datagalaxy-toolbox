from toolbox.commands.copy_links import copy_links
from toolbox.api.datagalaxy_api_workspaces import DataGalaxyApiWorkspace
from toolbox.api.http_client import HttpClient


# Mocks

def mock_list_links_on_source_workspace(self, workspace_name):
    if workspace_name == 'workspace_source':
        return ['link1', 'link2', 'link3']
    return []


# Scenarios

def test_copy_links_when_workspace_source_does_not_exist(mocker):
    # GIVEN
    workspaces = mocker.patch.object(DataGalaxyApiWorkspace, 'list_workspaces', autospec=True)
    workspaces.return_value = ['workspace_source']
    workspace_source_mock = mocker.patch.object(DataGalaxyApiWorkspace, 'get_workspace', autospec=True)
    workspace_source_mock.return_value = None

    # THEN
    http_client = HttpClient(verify_ssl=True)
    result = copy_links(
        url_source='url_source',
        token_source='token_source',
        url_target='url_target',
        token_target='token_target',
        workspace_source_name='workspace_source',
        version_source_name=None,
        workspace_target_name='workspace_target',
        version_target_name=None,
        http_client=http_client
    )

    # ASSERT / VERIFY

    assert result == 1
