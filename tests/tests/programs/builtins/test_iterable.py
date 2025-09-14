from tests.tests.programs.test_petl_program import get_petl_program_stdout


directory_prefix = "resources/programs/builtins/iterable"


def test_len(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/len.petl", mocker, capsys) == """3"""


def test_zip(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/zip.petl", mocker, capsys) == """[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]"""
