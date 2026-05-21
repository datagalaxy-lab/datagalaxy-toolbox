import json

from toolbox.api.datagalaxy_api_modules import DataGalaxyApiModules
from toolbox.api.http_client import HttpClient
from toolbox.commands.export_module import export_module


TIMESTAMP = "20260525_120000"


def read_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def freeze_export_timestamp(mocker):
    datetime_mock = mocker.patch("toolbox.commands.export_module.datetime")
    datetime_mock.now.return_value.strftime.return_value = TIMESTAMP


def test_export_dictionary_writes_sources_children_and_keys(mocker, monkeypatch, tmp_path):
    # GIVEN
    monkeypatch.chdir(tmp_path)
    freeze_export_timestamp(mocker)
    mocker.patch(
        "toolbox.commands.export_module.config_workspace",
        return_value={"name": "workspace", "versionId": "version_id"},
    )

    source = {
        "id": "source_id",
        "name": "SAS silver",
        "path": "\\SAS silver",
        "type": "Source",
    }
    container = {
        "id": "container_id",
        "name": "Schema",
        "path": "\\SAS silver\\Schema",
    }
    parent_table = {
        "id": "parent_table_id",
        "name": "Customer",
        "path": "\\SAS silver\\Customer",
    }
    child_table = {
        "id": "child_table_id",
        "name": "Order",
        "path": "\\SAS silver\\Order",
    }
    field = {
        "id": "field_id",
        "name": "Customer id",
        "path": "\\SAS silver\\Customer\\ID",
    }
    primary_key = {
        "technicalName": "PK_CUSTOMER",
        "table": {"id": "parent_table_id"},
        "columns": [{"technicalName": "ID", "pkOrder": 1}],
    }
    foreign_key = {
        "technicalName": "FK_ORDER_CUSTOMER",
        "displayName": "Order to customer",
        "columns": [{"technicalName": "CUSTOMER_ID"}],
        "primaryKey": {"technicalName": "PK_CUSTOMER"},
        "parents": {
            "structure": {"id": "parent_table_id"},
            "columns": [{"technicalName": "ID"}],
        },
        "children": {
            "structure": {"id": "child_table_id"},
            "columns": [{"technicalName": "CUSTOMER_ID"}],
        },
    }

    list_objects_mock = mocker.patch.object(DataGalaxyApiModules, "list_objects", autospec=True)
    list_objects_mock.return_value = [[source]]

    def list_children_objects(self, workspace_name, parent_id, object_type, include_links=False):
        children_by_type = {
            "containers": [[container]],
            "structures": [[parent_table, child_table]],
            "fields": [[field]],
        }
        return children_by_type[object_type]

    list_children_objects_mock = mocker.patch.object(
        DataGalaxyApiModules,
        "list_children_objects",
        autospec=True,
        side_effect=list_children_objects,
    )

    def list_keys(self, workspace_name, source_id, mode):
        if mode == "primary":
            return [primary_key]
        return [foreign_key]

    list_keys_mock = mocker.patch.object(DataGalaxyApiModules, "list_keys", autospec=True, side_effect=list_keys)

    # THEN
    http_client = HttpClient(verify_ssl=True)
    result = export_module(
        module="Dictionary",
        url="url",
        token="token",
        workspace_name="workspace",
        version_name=None,
        http_client=http_client,
    )

    # ASSERT / VERIFY
    export_dir = tmp_path / "export"

    assert result == 0
    assert list_objects_mock.call_count == 1
    assert list_children_objects_mock.call_count == 3
    assert list_keys_mock.call_count == 2
    assert sorted(path.name for path in export_dir.iterdir()) == [
        f"workspace_Dictionary_0_sources_{TIMESTAMP}.json",
        f"workspace_Dictionary_SAS silver_1_containers_{TIMESTAMP}.json",
        f"workspace_Dictionary_SAS silver_2_structures_{TIMESTAMP}.json",
        f"workspace_Dictionary_SAS silver_3_fields_{TIMESTAMP}.json",
        f"workspace_Dictionary_SAS silver_4_pks_{TIMESTAMP}.json",
        f"workspace_Dictionary_SAS silver_5_fks_{TIMESTAMP}.json",
    ]
    assert read_json(export_dir / f"workspace_Dictionary_0_sources_{TIMESTAMP}.json") == [source]
    assert read_json(export_dir / f"workspace_Dictionary_SAS silver_1_containers_{TIMESTAMP}.json") == [container]
    assert read_json(export_dir / f"workspace_Dictionary_SAS silver_2_structures_{TIMESTAMP}.json") == [parent_table, child_table]
    assert read_json(export_dir / f"workspace_Dictionary_SAS silver_3_fields_{TIMESTAMP}.json") == [field]
    assert read_json(export_dir / f"workspace_Dictionary_SAS silver_4_pks_{TIMESTAMP}.json") == [
        {
            "tablePath": "\\Customer",
            "columnName": "ID",
            "pkName": "PK_CUSTOMER",
            "pkOrder": 1,
        }
    ]
    assert read_json(export_dir / f"workspace_Dictionary_SAS silver_5_fks_{TIMESTAMP}.json") == [
        {
            "fkTechnicalName": "FK_ORDER_CUSTOMER",
            "pkTechnicalName": "PK_CUSTOMER",
            "pkTablePath": "\\Customer",
            "pkColumnName": "ID",
            "fkTablePath": "\\Order",
            "fkColumnName": "CUSTOMER_ID",
            "fkDisplayName": "Order to customer",
        }
    ]


def test_export_dataprocessing_normalizes_items_before_writing_export(mocker, monkeypatch, tmp_path):
    # GIVEN
    monkeypatch.chdir(tmp_path)
    freeze_export_timestamp(mocker)
    mocker.patch(
        "toolbox.commands.export_module.config_workspace",
        return_value={"name": "workspace", "versionId": "version_id"},
    )

    data_processing = {
        "id": "dp_id",
        "name": "Prepare customers",
        "type": "DataProcessing",
    }
    data_flow = {
        "id": "data_flow_id",
        "name": "Customer flow",
        "type": "DataFlow",
    }
    item = {
        "id": "item_id",
        "name": "Lookup customer",
        "type": "Search",
        "summary": None,
        "inputs": [{"path": "\\SAS silver\\Customer\\ID"}],
        "outputs": [{"path": "\\CRM\\Customer\\ID"}],
    }

    list_objects_mock = mocker.patch.object(DataGalaxyApiModules, "list_objects", autospec=True)
    list_objects_mock.return_value = [[data_processing, data_flow]]
    list_object_items_mock = mocker.patch.object(DataGalaxyApiModules, "list_object_items", autospec=True)
    list_object_items_mock.return_value = [item]

    # THEN
    http_client = HttpClient(verify_ssl=True)
    result = export_module(
        module="DataProcessing",
        url="url",
        token="token",
        workspace_name="workspace",
        version_name=None,
        http_client=http_client,
    )

    # ASSERT / VERIFY
    exported_objects = read_json(tmp_path / "export" / f"workspace_DataProcessing_{TIMESTAMP}.json")

    assert result == 0
    assert list_objects_mock.call_count == 1
    assert list_object_items_mock.call_count == 1
    assert exported_objects == [
        {
            "id": "dp_id",
            "name": "Prepare customers",
            "type": "DataProcessing",
            "dataProcessingItems": [
                {
                    "id": "item_id",
                    "name": "Lookup customer",
                    "type": "Lookup",
                    "summary": "",
                    "inputs": [
                        {
                            "path": "\\SAS silver\\Customer\\ID",
                            "entityPath": "\\SAS silver\\Customer\\ID",
                        }
                    ],
                    "outputs": [
                        {
                            "path": "\\CRM\\Customer\\ID",
                            "entityPath": "\\CRM\\Customer\\ID",
                        }
                    ],
                }
            ],
        },
        data_flow,
    ]
