import pytest
from portcast_app.utils import (
    SqlHelper,
    InvalidField,
    MissingKey
    )


@pytest.fixture()
def setup():
    instance = SqlHelper()
    sql_metadata = {
        'prep_stmt': (
            'SELECT * FROM test '
            'WHERE '
            'name = {0} '
            'AND id = {1} '
            'AND colors IN ({2}) '
            'AND first_name = {0}'
        ),
        'sql_helper': ['name', 'id', 'colors']
        }
    return (instance, sql_metadata)


def test_values_for_string_replacement():
    instance = SqlHelper()
    assert instance.format_input('hello') == '"hello"'
    assert instance.format_input(123) == 123
    assert instance.format_input(123.456) == 123.456


def test_invalid_values_for_string_replacement():
    instance = SqlHelper()
    with pytest.raises(InvalidField) as exc:
        instance.format_input({'hello': 'world'})
    assert str(exc.value) == "invalid datatype passed: <class 'dict'>"

    with pytest.raises(InvalidField) as exc:
        instance.format_input(['hello', 'world'])
    assert str(exc.value) == "invalid datatype passed: <class 'list'>"
    

def test_replace(setup):
    instance, sql_metadata = setup
    payload = {
        'name': 'john',
        'id': 12345,
        'colors': ['red', 'green', 'blue']
        }

    instance.replace(sql_metadata, payload)
    assert instance._prep_stmt == (
        'SELECT * FROM test '
        'WHERE '
        'name = "john" '
        'AND id = 12345 '
        'AND colors IN ("red","green","blue") '
        'AND first_name = "john"'
        )


def test_replace_invalid_key(setup):
    instance, sql_metadata = setup
    payload = {
        'random': 'john',
        'id': 12345,
        'colors': ['red', 'green', 'blue']
        }

    with pytest.raises(MissingKey) as exc:
        instance.replace(sql_metadata, payload)
    assert str(exc.value) == 'missing key for string replacement: name'


def test_generate_insert():
    instance = SqlHelper()
    entries = [
        {
        'name': 'john',
        'id': 12345,
        },
        {
        'name': 'kelly',
        'id': 6789,
        },
        ]
    instance.generate_insert('testing', entries)
    assert instance._prep_stmt == (
        'INSERT INTO testing '
        '(name,id) '
        'VALUES '
        '("john",12345),'
        '("kelly",6789)'
        )


def test_invalid_insert():
    instance = SqlHelper()
    entries = [
        {
        'name': 'john',
        'id': 12345,
        },
        'hello world'
        ]
    
    with pytest.raises(InvalidField) as exc:   
        instance.generate_insert('testing', entries)
    assert str(exc.value) == 'entries must be a list of dicts'

    entries2 = [
        {
        'name': 'john',
        'id': 12345,
        },
        {
        'random': 'kelly',
        'id': 6789,
        },
        ]

    with pytest.raises(MissingKey) as exc:   
        instance.generate_insert('testing', entries2)
    assert str(exc.value) == 'missing key for sql parsing: name'
