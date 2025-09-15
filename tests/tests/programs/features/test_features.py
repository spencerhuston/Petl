from tests.tests.programs.test_petl_program import get_petl_program_stdout

directory_prefix = "resources/programs/features"


def test_alias(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/alias.petl", mocker, capsys) == """Alice\n25\n$75,000\n\nBob\n30\n$80,000\n\nMark\n23\n$50,000"""


def test_bird_operator(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/bird_operator.petl", mocker, capsys) == """3"""


def test_plus_operator(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/plus_operator.petl", mocker, capsys) == """8"""


def test_multiple_prim_ops(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/multiple_prim_ops.petl", mocker, capsys) == """8\n2"""


def test_stack_trace_test(mocker, capsys):
    assert "Type mismatch" in get_petl_program_stdout(f"{directory_prefix}/stack_trace_test.petl", mocker, capsys)


def test_union_type(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/union_type.petl", mocker, capsys) == """false"""


def test_unpack_tuple(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/unpack_tuple.petl", mocker, capsys) == """5\n3\nb\n3"""
