import json

from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.http_client import HttpClient
from toolbox.commands.export_links import export_links


TIMESTAMP = "20260525_121508"


def read_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def test_export_links_writes_links_found_on_dictionary_children(mocker, monkeypatch, tmp_path):
    # GIVEN
    monkeypatch.chdir(tmp_path)
    datetime_mock = mocker.patch("toolbox.commands.export_links.datetime")
    datetime_mock.now.return_value.strftime.return_value = TIMESTAMP
    mocker.patch(
        "toolbox.commands.export_links.config_workspace",
        return_value={"name": "workspace", "versionId": "version_id"},
    )

    glossary_object = {
        "id": "glossary_id",
        "path": "\\Glossary\\Customer",
        "typePath": "\\Glossary\\Term",
        "links": {},
    }
    dictionary_source = {
        "id": "source_id",
        "path": "\\SAS silver",
        "typePath": "\\Source",
        "links": {},
    }
    data_processing = {
        "id": "data_processing_id",
        "path": "\\Prepare customers",
        "typePath": "\\DataProcessing",
        "links": {},
    }
    usage = {
        "id": "usage_id",
        "path": "\\Customer report",
        "typePath": "\\Usage",
        "links": {},
    }
    field = {
        "id": "field_id",
        "path": "\\SAS silver\\Customer\\ID",
        "typePath": "\\Source\\Table\\Field",
        "links": {
            "documents": [
                {
                    "path": "\\Glossary\\Customer",
                    "typePath": "\\Glossary\\Term",
                }
            ]
        },
    }

    def list_objects(self, workspace_name, include_links=False):
        objects_by_module = {
            "Glossary": [[glossary_object]],
            "Dictionary": [[dictionary_source]],
            "DataProcessing": [[data_processing]],
            "Uses": [[usage]],
        }
        return objects_by_module[self.module]

    list_objects_mock = mocker.patch.object(DataGalaxyApiModules, "list_objects", autospec=True, side_effect=list_objects)

    def list_children_objects(self, workspace_name, parent_id, object_type, include_links=False):
        children_by_type = {
            "containers": [[]],
            "structures": [[]],
            "fields": [[field]],
        }
        return children_by_type[object_type]

    list_children_objects_mock = mocker.patch.object(
        DataGalaxyApiModules,
        "list_children_objects",
        autospec=True,
        side_effect=list_children_objects,
    )

    # THEN
    http_client = HttpClient(verify_ssl=True)
    result = export_links(
        url="url",
        token="token",
        workspace_name="workspace",
        version_name=None,
        http_client=http_client,
    )

    # ASSERT / VERIFY
    exported_links = read_json(tmp_path / "export" / f"workspace_links_{TIMESTAMP}.json")

    assert result == 0
    assert list_objects_mock.call_count == 4
    assert list_children_objects_mock.call_count == 3
    assert all(call.kwargs["include_links"] is True for call in list_objects_mock.call_args_list)
    assert all(call.kwargs["include_links"] is True for call in list_children_objects_mock.call_args_list)
    assert exported_links == [
        {
            "fromPath": "\\SAS silver\\Customer\\ID",
            "fromType": "\\Source\\Table\\Field",
            "linkType": "documents",
            "toPath": "\\Glossary\\Customer",
            "toType": "\\Glossary\\Term",
        }
    ]
