import pytest as pytest
from toolbox.api.datagalaxy_api_attributes import to_bulk_item_attribute


def test_with_too_many_fields():
    attribute = {
        'name': 'Custom Property',
        'attributeKey': 'allCustomProp105',
        'format': 'MultiValueList',
        'description': 'New Custom property',
        'isCustom': True,
        'isMandatory': False,
        'isEditable': True
    }
    expected = {
        'name': 'Custom Property',
        'format': 'MultiValueList',
        'description': 'New Custom property'
    }
    assert to_bulk_item_attribute(attribute) == expected


def test_without_required_fields():
    attribute = {
        'attributeKey': 'allCustomProp105',
        'format': 'MultiValueList',
        'description': 'New Custom property',
        'isCustom': True,
        'isMandatory': False,
        'isEditable': True
    }
    with pytest.raises(Exception, match=f'name is missing on {attribute} attribute'):
        to_bulk_item_attribute(attribute)
