from tests.programs.test_petl_program import get_petl_program_stdout


directory_prefix = "builtins/functional"


def test_filter(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/filter.petl", mocker, capsys) == """[2, 4, 6, 8, 10]"""


def test_foldl(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/foldl.petl", mocker, capsys) == """3628800"""


def test_map(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/map.petl", mocker, capsys) == """[2, 3, 4]"""
