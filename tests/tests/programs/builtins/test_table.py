import os.path
from pathlib import Path

from tests.tests.programs.test_petl_program import get_petl_program_stdout

directory_prefix = "tests/resources/programs/builtins/table"


def test_collect(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/collect.petl", mocker, capsys) == """(Alice, 27, $60000)\n(Bob, 45, $100000)\n(Mark, 23, $45000)"""


def test_get_columns(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/get_columns.petl", mocker, capsys) == """[(Alice, 27), (Bob, 45), (Mark, 23)]"""


def test_get_column(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/get_column.petl", mocker, capsys) == """[Alice, Bob, Mark]"""


def test_get_column_does_not_exist(mocker, capsys):
    assert """Column 'test' does not exist in this table""" in get_petl_program_stdout(f"{directory_prefix}/get_column_does_not_exist.petl", mocker, capsys)


def test_count(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/count.petl", mocker, capsys) == """3"""


def test_create_table(mocker, capsys):
    create_table_result = get_petl_program_stdout(f"{directory_prefix}/createTable.petl", mocker, capsys)
    assert "Bob" in create_table_result and "45" in create_table_result and "$100000" in create_table_result


def test_drop(mocker, capsys):
    drop_result = get_petl_program_stdout(f"{directory_prefix}/drop.petl", mocker, capsys)
    assert "Bob" in drop_result and "45" in drop_result and "$100000" not in drop_result


def test_read_csv(mocker, capsys):
    read_csv_result = get_petl_program_stdout(f"{directory_prefix}/readCsv.petl", mocker, capsys)
    assert "Bob" in read_csv_result and "45" in read_csv_result and "$100000" in read_csv_result


def test_write_csv(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/writeCsv.petl", mocker, capsys) == "Created successfully"
    csv_path = Path("resources/csvs/test_write.csv")
    if os.path.exists(csv_path):
        os.remove(csv_path)


def test_with(mocker, capsys):
    read_csv_result = get_petl_program_stdout(f"{directory_prefix}/with.petl", mocker, capsys)
    assert "Bob" in read_csv_result and "45" in read_csv_result and "$100000" in read_csv_result


def test_join(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/join.petl", mocker, capsys) == """[(Alice, 27), (Bob, 45)]"""


def test_join_duplicate_name(mocker, capsys):
    assert "must be unique across both tables" in get_petl_program_stdout(f"{directory_prefix}/join_duplicate_name.petl", mocker, capsys)


def test_select(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/select.petl", mocker, capsys) == """[(Alice, 27), (Bob, 45)]"""


def test_column(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/column.petl", mocker, capsys) == """[(1), (2), (3)]"""


def test_append(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/append.petl", mocker, capsys) == """(Eve, 30, $75000)"""
