def test_dummy_islist(dummy_data):
    assert type(dummy_data) == list, \
        'Should be a list'


def test_dummy_nonempty(dummy_data):
    assert len(dummy_data) > 0, \
        'Should be a a non-empty list'


def test_dummy_nozeros(dummy_data):
    assert not 0 in dummy_data, \
        'Should be a list'
