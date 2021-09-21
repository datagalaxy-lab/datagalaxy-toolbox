from toolbox.api.datagalaxy_api_workspaces import del_useless_keys


def test_del_useless_keys_with_too_many_keys():
    data = {
        "type": "",
        "status": "",
        "owners": "",
        "stewards": "",
        "tags": "",
        "description": "",
        "summary": "",
        "code": "",
        "name": "",
        "children": "",
        "property1": "",
        "property2": "",
        'lastModificationTime': "",
        'attributes': ""
    }
    result = {
        "type": "",
        "status": "",
        "owners": "",
        "stewards": "",
        "tags": "",
        "description": "",
        "summary": "",
        "code": "",
        "name": "",
        "children": "",
        "property1": "",
        "property2": "",
    }
    assert del_useless_keys(data) == result
