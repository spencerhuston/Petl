from tests.tests.programs.test_petl_program import get_petl_program_stdout

directory_prefix = "resources/programs/examples"


def test_bigger_csv(mocker, capsys):
    bigger_csv_output = get_petl_program_stdout(f"{directory_prefix}/bigger_csv.petl", mocker, capsys)
    assert "Estelle" in bigger_csv_output and "Hughes" in bigger_csv_output and "pi@lof.vn" in bigger_csv_output and "50" in bigger_csv_output and "$2132"


def test_data_stream_example(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/data_stream_example.petl", mocker, capsys) == """[50000, 35000]"""


def test_table_doc_test(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/table_doc_test.petl", mocker, capsys) == """[60000, 100000, 45000]"""
