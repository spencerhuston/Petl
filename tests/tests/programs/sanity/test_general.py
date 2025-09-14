from tests.tests.programs.test_petl_program import get_petl_program_stdout


directory_prefix = "resources/programs/sanity/general"


def test_alias_tuple_type(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/alias_tuple_type.petl", mocker, capsys) == """(test, 100)"""


def test_comment_after_line(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/comment_after_line.petl", mocker, capsys) == """5"""


def test_comment_single_line(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/comment_single_line.petl", mocker, capsys) == """test"""


def test_env(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/env.petl", mocker, capsys) == """5"""


def test_multiple_integer_literal_lets(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/multiple_integer_literal_lets.petl", mocker, capsys) == """1\n2"""


def test_shadowing(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/shadowing.petl", mocker, capsys) == """2\n3"""


def test_single_integer_literal(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/single_integer_literal.petl", mocker, capsys) == """test"""


def test_single_integer_literal_let(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/single_integer_literal_let.petl", mocker, capsys) == """1"""


def test_single_let_range_definition(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/single_let_range_definition.petl", mocker, capsys) == """[0, 1, 2, 3, 4, 5]"""


#def test_stress(mocker, capsys):
    #assert get_petl_program_stdout(f"{directory_prefix}/stress.petl", mocker, capsys).startswith("[")


def test_type_mismatch_integer_literal_char_literal(mocker, capsys):
    assert not get_petl_program_stdout(f"{directory_prefix}/type_mismatch_integer_literal_char_literal.petl", mocker, capsys) == """"""


def test_collection_parse_no_comma_error(mocker, capsys):
    assert "Expected ), got (" in get_petl_program_stdout(f"{directory_prefix}/collection_parse_no_comma_error.petl", mocker, capsys)
