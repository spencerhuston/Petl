from tests.programs.test_petl_program import get_petl_program_stdout


directory_prefix = "builtins/int"


def test_min_max(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/min_max.petl", mocker, capsys) == """50\n25"""


def test_sort(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/sort.petl", mocker, capsys) == """[1, 2, 4, 5, 6, 8, 9]"""


def test_string_to_int(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/stringToInt.petl", mocker, capsys) == """int"""


def test_sum_product(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/sum_product.petl", mocker, capsys) == """15\n120"""
