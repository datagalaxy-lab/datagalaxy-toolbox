from toolbox.api.datagalaxy_api_screens import DataGalaxyApiScreen
from toolbox.api.http_client import HttpClient
from toolbox.commands.copy_screens import copy_screens
import pytest as pytest


def test_copy_screens_when_no_screen(mocker):
    """
    Scenario 1. error
    :param mocker:
    :return: raise Exception
    """
    source_screens_list_mock = mocker.patch.object(DataGalaxyApiScreen, 'list_screens', autospec=True)
    source_screens_list_mock.return_value = []

    # ASSERT / VERIFY
    http_client = HttpClient(verify_ssl=True)
    with pytest.raises(Exception, match='Unexpected error: source has no screen'):
        copy_screens(
            url_source='url_source',
            url_target='url_target',
            token_source='token_source',
            token_target='token_target',
            workspace_source_name=None,
            workspace_target_name=None,
            http_client=http_client
        )
