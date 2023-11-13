from toolbox.api.datagalaxy_api import DataGalaxyApiAuthentication, Token
from toolbox.api.datagalaxy_api_screens import DataGalaxyApiScreen
from toolbox.commands.copy_screens import copy_screens
import pytest as pytest


def test_copy_screens_when_no_screen(mocker):
    """
    Scenario 1. error
    :param mocker:
    :return: raise Exception
    """
    client_space_mock = mocker.patch.object(Token, 'get_client_space_id', autospec=True)
    client_space_mock.return_value = 'cid'
    api_authenticate_mock = mocker.patch.object(DataGalaxyApiAuthentication, 'authenticate', autospec=True)
    api_authenticate_mock.return_value = 'token'
    source_screens_list_mock = mocker.patch.object(DataGalaxyApiScreen, 'list_screens', autospec=True)
    source_screens_list_mock.return_value = []

    # ASSERT / VERIFY
    with pytest.raises(Exception, match='Unexpected error: source has no screen'):
        copy_screens(
            url_source='url_source',
            url_target='url_target',
            token_source='token_source',
            token_target='token_target',
            workspace_source_name=None,
            workspace_target_name=None
        )
