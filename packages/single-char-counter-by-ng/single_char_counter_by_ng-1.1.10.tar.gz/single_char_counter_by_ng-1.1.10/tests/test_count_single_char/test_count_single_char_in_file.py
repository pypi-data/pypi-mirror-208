import pytest

from unittest.mock import patch, mock_open

from . import (param_good_case_insensitive_false,
               param_good_case_insensitive_true,
               param_with_typeerror,
               count_single_char_in_file,
               )


@pytest.mark.parametrize("data", param_with_typeerror)
def test_count_single_char_in_file_typeeror(data):
    with pytest.raises(TypeError):
        count_single_char_in_file(data)


def test_count_single_char_in_file_filenotfound():
    path_to_file = "test/test/test.txt"
    with pytest.raises(FileNotFoundError):
        count_single_char_in_file(path_to_file)


@pytest.mark.parametrize("data, expected", param_good_case_insensitive_false)
def test_count_single_char_in_file_good_ci_false(data, expected):
    mock_file = mock_open(read_data=data)
    with patch("builtins.open", mock_file):
        assert count_single_char_in_file('test.txt') == expected


@pytest.mark.parametrize("data, expected", param_good_case_insensitive_true)
def test_count_single_char_in_file_good_ci_true(data, expected):
    mock_file = mock_open(read_data=data)
    with patch("builtins.open", mock_file):
        assert count_single_char_in_file(
            'test.txt', case_insensitive=True) == expected
