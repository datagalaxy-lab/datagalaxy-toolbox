from toolbox.api.datagalaxy_api_technologies import DataGalaxyApiTechnology
from toolbox.commands.copy_technologies import copy_technologies
import pytest as pytest


def list_mock_technologies_without_custom():
    return [
        {
            'creationUserId': '00000000-0000-0000-0000-000000000000',
        }
    ]


def test_copy_technologies_when_nothing_on_source(mocker):
    """
    Scenario 1. error
    :param mocker:
    :return: raise Exception
    """
    technologies_list_mock = mocker.patch.object(DataGalaxyApiTechnology, 'list_technologies', autospec=True)
    technologies_list_mock.return_value = []

    # ASSERT / VERIFY
    with pytest.raises(Exception, match='no technology found on source clientspace'):
        copy_technologies(
            url_source='url_source',
            url_target='url_target',
            token_source='token_source',
            token_target='token_target'
        )


def test_copy_technologies_when_no_custom_technology_on_source(mocker):
    """
    Scenario 1. error
    :param mocker:
    :return: raise Exception
    """
    technologies_list_mock = mocker.patch.object(DataGalaxyApiTechnology, 'list_technologies', autospec=True)
    technologies_list_mock.return_value = list_mock_technologies_without_custom()

    # ASSERT / VERIFY
    result = copy_technologies(
            url_source='url_source',
            url_target='url_target',
            token_source='token_source',
            token_target='token_target'
        )

    assert result == 0
