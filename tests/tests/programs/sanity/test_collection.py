from tests.tests.programs.test_petl_program import get_petl_program_stdout


directory_prefix = "resources/examples/programs/sanity/collection"


def test_dict_definition_app(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/dict_definition_app.petl", mocker, capsys) == """1"""


def test_empty_tuple(mocker, capsys):
    assert not get_petl_program_stdout(f"{directory_prefix}/empty_tuple.petl", mocker, capsys) == """"""


def test_list_app(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/list_app.petl", mocker, capsys) == """3"""


def test_list_app_in_lambda_app(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/list_app_in_lambda_app.petl", mocker, capsys) == """1"""


def test_nested_list_application(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/nested_list_application.petl", mocker, capsys) == """1"""


def test_nested_list_application_type_mismatch(mocker, capsys):
    assert not get_petl_program_stdout(f"{directory_prefix}/nested_list_application_type_mismatch.petl", mocker, capsys) == """"""


def test_nested_tuple_application(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/nested_tuple_application.petl", mocker, capsys) == """1"""


def test_nested_tuple_application_type_mismatch(mocker, capsys):
    assert not get_petl_program_stdout(f"{directory_prefix}/nested_tuple_application_type_mismatch.petl", mocker, capsys) == """"""


def test_single_let_list_of_integer_literals(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/single_let_list_of_integer_literals.petl", mocker, capsys) == """[0, 1, 2, 3, 4]"""


def test_type_mismatch_tuple_def(mocker, capsys):
    assert not get_petl_program_stdout(f"{directory_prefix}/type_mismatch_tuple_def.petl", mocker, capsys) == """1"""


def test_tuple_unpack(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/tuple_unpack.petl", mocker, capsys) == """0\na\ntrue"""
