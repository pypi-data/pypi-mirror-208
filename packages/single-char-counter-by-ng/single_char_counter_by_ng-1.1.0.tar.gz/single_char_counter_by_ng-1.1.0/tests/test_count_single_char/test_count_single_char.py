import pytest

from typing import Any

from . import (count_single_char,
               param_good_case_insensitive_false,
               param_good_case_insensitive_true,
               param_with_typeerror,
               param_for_cache,
               )


@pytest.mark.parametrize("data, expected", param_good_case_insensitive_false)
def test_count_single_char_good_case_sensitive_true(data: str, expected: int):
    result = count_single_char(data)
    assert result == expected


@pytest.mark.parametrize("data, expected", param_good_case_insensitive_true)
def test_count_single_char_good_case_sensitive_false(data: str, expected: int):
    result = count_single_char(data, case_insensitive=True)
    assert result == expected


@pytest.mark.parametrize("data", param_with_typeerror)
def test_count_single_char_typeerror(data: Any):
    with pytest.raises(TypeError):
        count_single_char(data)


@pytest.mark.parametrize("data, number_of_add", param_for_cache)
def test_cache_in_count_single_char(data: str, number_of_add):
    cache_len_before = count_single_char.cache_info().currsize
    count_single_char(data)
    cache_len_after = count_single_char.cache_info().currsize
    expected_cache_len = cache_len_before + number_of_add
    assert cache_len_after == expected_cache_len
