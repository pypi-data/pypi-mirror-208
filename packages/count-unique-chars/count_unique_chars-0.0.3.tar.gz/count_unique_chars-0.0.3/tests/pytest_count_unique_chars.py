from collections import Counter

import pytest
from pytest_mock import MockerFixture

from src.count_unique_chars.count_unique_chars import UniqueCharsCounter
from src.count_unique_chars.exceptions import TypeNotStrException


@pytest.mark.parametrize("input_string, expected_value", [
    ('abbbccdf', 3),
    ('11233454', 2),
    ('aaa', 0),
    ('', 0)
])
def test_count_unique_chars_typical_behavior(input_string: str, expected_value: int):
    unique_chars_counter = UniqueCharsCounter()
    assert unique_chars_counter.count_unique_chars(input_string) == expected_value
    assert unique_chars_counter.cache[input_string] == expected_value


@pytest.mark.parametrize("invalid_input", [1, True, [1], {1}, {'1': 1}, (1,), frozenset([1])])
def test_count_unique_chars_atypical_behavior(invalid_input: any):
    with pytest.raises(TypeNotStrException):
        UniqueCharsCounter().count_unique_chars(invalid_input)


def test_count_unique_chars_caching(mocker: MockerFixture):
    input_text = '111223'
    return_value = 1
    unique_chars_counter = UniqueCharsCounter()
    unique_chars_counter.cache[input_text] = return_value
    mocker.patch.object(Counter, 'values')
    assert unique_chars_counter.count_unique_chars(input_text) == return_value
    Counter.values.assert_not_called()
