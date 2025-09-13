from tests.programs.test_petl_program import get_petl_program_stdout

directory_prefix = "builtins/table"


def test_collect(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/collect.petl", mocker, capsys) == """(Alice, 27, $60000)\n(Bob, 45, $100000)\n(Mark, 23, $45000)"""


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
