from toolbox.api.datagalaxy_api import to_bulk_tree


def test_transform_ok():
    properties = [
        {
            "name": "Green",
            "technicalName": "Green",
            "path": "\\Orange\\Red\\Green",
            "type": "Concept",
            "typePath": "\\Universe\\Universe\\Concept"
        },
        {
            "name": "Red",
            "technicalName": "Red",
            "path": "\\Orange\\Red",
            "type": "Universe",
            "typePath": "\\Universe\\Universe"
        },
        {
            "name": "Orange",
            "technicalName": "Orange",
            "path": "\\Orange",
            "type": "Universe",
            "typePath": "\\Universe",
            "attributes": {
                "status": "Proposed",
                "tags": [],
                "summary": "string",
                "description": "string",
                "owners": [],
                "stewards": [],
                "creationTime": "string",
                "lastModificationTime": "string",
                "property1": "string",
                "property2": "string"
            }
        },
        {
            "name": "Grey",
            "technicalName": "Grey",
            "path": "\\Orange\\Grey",
            "type": "Concept",
            "typePath": "\\Universe\\Universe"
        }
    ]
    expected = [
        {
            "type": "Universe",
            "name": "Orange",
            "technicalName": "Orange",
            "status": "Proposed",
            "tags": [],
            "summary": "string",
            "description": "string",
            "owners": [],
            "stewards": [],
            "property1": "string",
            "property2": "string",
            "children": [
                {
                    "type": "Universe",
                    "name": "Red",
                    "technicalName": "Red",
                    "children": [
                        {
                            "type": "Concept",
                            "name": "Green",
                            "technicalName": "Green",
                        }
                    ]
                },
                {
                    "type": "Concept",
                    "name": "Grey",
                    "technicalName": "Grey",
                }
            ]
        }
    ]
    assert to_bulk_tree(properties) == expected
