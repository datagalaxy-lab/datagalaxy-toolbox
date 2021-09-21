from toolbox.api.datagalaxy_api_attributes import _get_name


def test__get_name():
    attribute = {
        'name': 'foo',
        'attributeKey': 'DisplayName',
        'format': 'Text',
        'description': '',
        'isCustom': False,
        'isMandatory': True,
        'isEditable': True
    }
    assert _get_name(attribute) == 'foo'
