import sys

import pytest

from count_unique_chars.cli import main, create_parser


@pytest.fixture
def mocker_file(mocker):
    mocked_file_data = mocker.mock_open(read_data="abc")
    mocker.patch("builtins.open", mocked_file_data)


def test_create_parser(mocker):
    mocker.patch.object(sys, 'argv', ['main.py', '--file', 'test.txt', '--string', 'abc'])
    parser = create_parser()
    args = parser.parse_args()
    assert args.file == 'test.txt'
    assert args.string == 'abc'


@pytest.mark.parametrize("arg, expected_output", [
    (['main.py', '--file', 'test.txt'], 'Number of unique characters: 3\n'),
    (['main.py', '--string', 'abcde'], 'Number of unique characters: 5\n'),
    (['main.py', '--file', 'test.txt', '--string', 'abcde'], 'Number of unique characters: 3\n')
])
def test_main_with_cli_arguments(mocker, mocker_file, capfd, arg, expected_output):
    mocker.patch.object(sys, 'argv', arg)
    main()
    captured = capfd.readouterr()
    assert captured.out == expected_output


def test_main_file_not_found_error_message(mocker, capsys):
    mocker.patch.object(sys, 'argv', ['main.py', '--file', 'nonexistent.txt'])
    with pytest.raises(SystemExit):
        main()
    assert 'File not found.' in capsys.readouterr().err
