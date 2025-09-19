from tests.tests.programs.test_petl_program import get_petl_program_stdout


directory_prefix = "resources/examples/programs/sanity/lambda"


def test_lambda_closure(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/lambda_closure.petl", mocker, capsys) == """7"""


def test_mutually_recursive(mocker, capsys):
    assert not get_petl_program_stdout(f"{directory_prefix}/mutually_recursive.petl", mocker, capsys) == """"""


def test_nested_lambda_closure(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/nested_lambda_closure.petl", mocker, capsys) == """5\n3"""


def test_single_lambda_def_no_args_single_ref(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/single_lambda_def_no_args_single_ref.petl", mocker, capsys) == """5"""


def test_single_lambda_def_no_args_single_ref_type_mismatch(mocker, capsys):
    assert "Type mismatch" in get_petl_program_stdout(f"{directory_prefix}/single_lambda_def_no_args_single_ref_type_mismatch.petl", mocker, capsys)


def test_single_lambda_def_single_arg_single_ref(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/single_lambda_def_single_arg_single_ref.petl", mocker, capsys) == """4"""


def test_single_lambda_def_single_arg_single_ref_type_mismatch(mocker, capsys):
    assert "Type mismatch" in get_petl_program_stdout(f"{directory_prefix}/single_lambda_def_single_arg_single_ref_type_mismatch.petl", mocker, capsys)
