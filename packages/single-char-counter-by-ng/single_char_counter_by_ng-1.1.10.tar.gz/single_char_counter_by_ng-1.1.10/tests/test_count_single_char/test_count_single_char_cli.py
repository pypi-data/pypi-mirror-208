import pytest

from unittest.mock import patch, mock_open

from single_char_counter_by_ng import parse_arguments
from . import (param_good_case_insensitive_false,
               param_good_case_insensitive_true,
               count_single_char_cli,
               )


@pytest.mark.parametrize("data, expected", param_good_case_insensitive_false)
def test_count_single_char_cli_file_ci_false(monkeypatch, capsys, data, expected):
    args = ["--file", "test.txt"]
    mock_file = mock_open(read_data=data)
    
    with patch("builtins.open", mock_file):
        monkeypatch.setattr("sys.argv", ["count_single_char_cli.py"] + args)
        count_single_char_cli(parse_arguments())
        captured = capsys.readouterr()
        result = int(captured.out.strip())
        assert result == expected


@pytest.mark.parametrize("data, expected", param_good_case_insensitive_true)
def test_count_single_char_cli_file_ci_true(monkeypatch, capsys, data, expected):
    args = ["--file", "test.txt", "-i"]
    mock_file = mock_open(read_data=data)
    
    with patch("builtins.open", mock_file):
        monkeypatch.setattr("sys.argv", ["count_single_char_cli.py"] + args)        
        count_single_char_cli(parse_arguments())
        captured = capsys.readouterr()
        result = int(captured.out.strip())
        assert result == expected


@pytest.mark.parametrize("data, expected", param_good_case_insensitive_false)
def test_count_single_char_cli_string_ci_false(monkeypatch, capsys, data, expected):
    args = ["--string", data]
    
    if data:
        monkeypatch.setattr("sys.argv", ["count_single_char_cli.py"] + args)
        count_single_char_cli(parse_arguments())
        captured = capsys.readouterr()
        result = int(captured.out.strip())
        assert result == expected


@pytest.mark.parametrize("data, expected", param_good_case_insensitive_true)
def test_count_single_char_cli_string_ci_true(monkeypatch, capsys, data, expected):
    args = ["--string", data, "-i"]

    if data:
        monkeypatch.setattr("sys.argv", ["count_single_char_cli.py"] + args)
        count_single_char_cli(parse_arguments())
        captured = capsys.readouterr()
        result = int(captured.out.strip())
        assert result == expected


def test_count_single_char_cli_no_input(monkeypatch, capsys):
    args = [] # No input in console
    expected_output = "No input specified. Please provide either --file or --string argument."
    
    monkeypatch.setattr("sys.argv", ["count_single_char_cli.py"] + args)
    count_single_char_cli(parse_arguments())
    captured = capsys.readouterr()
    result = captured.out.strip()
    assert result == expected_output
    

def test_count_single_char_cli_file_priority(monkeypatch, capsys):
    mock_file = mock_open(read_data="aaaAAbbB")
    args = ["--string", "AAAaas", "--file", "path_to_file"]
    expected_output = 1
    
    with patch("builtins.open", mock_file):
        monkeypatch.setattr("sys.argv", ["count_single_char_cli.py"] + args)
        count_single_char_cli(parse_arguments())
        captured = capsys.readouterr()
        result = int(captured.out.strip())
        assert result == expected_output
