from toolbox.api.datagalaxy_api_attributes import find_duplicates


def test_with_duplicate():
    result = find_duplicates(
        [
            {
                'name': 'address'
            }
        ],
        [
            {
                'name': 'address'
            },
            {
                'name': 'name'
            }
        ]
    )
    assert len(result) == 1


def test_without_duplicate():
    result = find_duplicates(
        [
            {
                'name': 'address'
            }
        ],
        [
            {
                'name': 'name'
            }
        ]
    )
    assert len(result) == 0
