from tests.tests.programs.test_petl_program import get_petl_program_stdout


directory_prefix = "tests/resources/programs/builtins/string"


def test_starts_ends_with(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/starts_ends_with.petl", mocker, capsys) == """true\ntrue\nfalse\nfalse"""


def test_str_toupper_tolower(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/str_toupper_tolower.petl", mocker, capsys) == """HELLO WORLD!\nhello world!"""


def test_substr(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/substr.petl", mocker, capsys) == """he"""


def test_to_string(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/toString.petl", mocker, capsys) == """500\ntrue"""
