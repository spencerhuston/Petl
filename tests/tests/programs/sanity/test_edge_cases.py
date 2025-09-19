from tests.tests.programs.test_petl_program import get_petl_program_stdout


directory_prefix = "resources/examples/programs/sanity/edge_cases"


def test_comments(mocker, capsys):
    assert "Invalid program, unable to parse" in get_petl_program_stdout(f"{directory_prefix}/comments.petl", mocker, capsys)


def test_control_flow(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/control_flow.petl", mocker, capsys) == """greater"""


def test_deeply_nested(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/deeply_nested.petl", mocker, capsys) == """3"""


def test_division_by_zero(mocker, capsys):
    assert "Division by zero" in get_petl_program_stdout(f"{directory_prefix}/division_by_zero.petl", mocker, capsys)


def test_duplicate_keys(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/duplicate_keys.petl", mocker, capsys) == "1"


def test_empty(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/empty.petl", mocker, capsys) == ""


def test_invalid_assignment(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/invalid_assignment.petl", mocker, capsys) == ""


def test_invalid_function_call(mocker, capsys):
    assert "Invalid argument count for function" in get_petl_program_stdout(f"{directory_prefix}/invalid_function_call.petl", mocker, capsys)


def test_invalid_lambda(mocker, capsys):
    assert "Expected type signature but received none" in get_petl_program_stdout(f"{directory_prefix}/invalid_lambda.petl", mocker, capsys)


def test_invalid_list_index(mocker, capsys):
    assert "Type mismatch: char vs. int" in get_petl_program_stdout(f"{directory_prefix}/invalid_list_index.petl", mocker, capsys)


def test_invalid_operator(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/invalid_operator.petl", mocker, capsys) == ""


def test_invalid_syntax(mocker, capsys):
    assert "Invalid expression found" in get_petl_program_stdout(f"{directory_prefix}/invalid_syntax.petl", mocker, capsys)


def test_long_identifier(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/long_identifier.petl", mocker, capsys) == ""


def test_missing_brace(mocker, capsys):
    assert "Expected }" in get_petl_program_stdout(f"{directory_prefix}/missing_brace.petl", mocker, capsys)


def test_undefined_variable(mocker, capsys):
    assert "does not exist in this scope" in get_petl_program_stdout(f"{directory_prefix}/undefined_variable.petl", mocker, capsys)


def test_unicode_variable(mocker, capsys):
    assert "Unexpected character" in get_petl_program_stdout(f"{directory_prefix}/unicode_variable.petl", mocker, capsys)


def test_unexpected_token(mocker, capsys):
    assert "Invalid expression found" in get_petl_program_stdout(f"{directory_prefix}/unexpected_token.petl", mocker, capsys)


def test_nested_lets_invalid(mocker, capsys):
    assert "Invalid expression found" in get_petl_program_stdout(f"{directory_prefix}/nested_lets_invalid.petl", mocker, capsys)
