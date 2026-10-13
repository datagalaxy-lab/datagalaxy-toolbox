from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.http_client import HttpClient
from toolbox.commands.map_glossary_dictionary import map_glossary_dictionary


def call(file_path, http_client=None):
    return map_glossary_dictionary(
        url='url',
        token='token',
        workspace_name='workspace',
        version_name=None,
        file_path=str(file_path),
        glossary_column='Glossary',
        dictionary_column='Dictionary',
        http_client=http_client or HttpClient(verify_ssl=True)
    )


# Scenarios

def test_map_glossary_dictionary_when_workspace_does_not_exist(mocker, tmp_path):
    # GIVEN
    mocker.patch('toolbox.commands.map_glossary_dictionary.config_workspace', return_value=None)

    # THEN
    result = call(tmp_path / 'mapping.csv')

    # ASSERT / VERIFY
    assert result == 1


def test_map_glossary_dictionary_when_file_does_not_exist(mocker, tmp_path):
    # GIVEN
    mocker.patch('toolbox.commands.map_glossary_dictionary.config_workspace', return_value={'id': 'ws_id'})

    # THEN
    result = call(tmp_path / 'missing.csv')

    # ASSERT / VERIFY
    assert result == 1


def test_map_glossary_dictionary_creates_links(mocker, tmp_path):
    # GIVEN
    mocker.patch('toolbox.commands.map_glossary_dictionary.config_workspace', return_value={'id': 'ws_id'})
    mocker.patch.object(DataGalaxyApiModules, 'list_objects', autospec=True,
                        side_effect=lambda self, workspace_name, name: [[{'id': f'g_{name}'}]] if name == 'term' else [])
    mocker.patch.object(DataGalaxyApiModules, 'list_children_objects', autospec=True,
                        return_value=[[{'id': 'field1'}, {'id': 'field2'}]])
    bulk = mocker.patch.object(DataGalaxyApiModules, 'bulk_upsert_tree', autospec=True)

    mapping_file = tmp_path / 'mapping.csv'
    mapping_file.write_text(
        'Glossary,Dictionary\n'
        'term,col\n'
        'unknown,col\n'
        'term,\n',
        encoding='utf-8'
    )

    # THEN
    result = call(mapping_file)

    # ASSERT / VERIFY
    assert result == 0
    bulk.assert_called_once()
    assert bulk.call_args.kwargs['bulktree'] == [
        {'fromId': 'g_term', 'toId': 'field1', 'type': 'IsImplementedBy'},
        {'fromId': 'g_term', 'toId': 'field2', 'type': 'IsImplementedBy'},
    ]
    assert bulk.call_args.kwargs['links_by_id'] is True
