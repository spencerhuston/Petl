from tests.tests.programs.test_petl_program import get_petl_program_stdout


directory_prefix = "resources/examples/programs/sanity/for"


def test_for_loop_over_list_def_single_reference(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/for_loop_over_list_def_single_reference.petl", mocker, capsys) == """0\n1\n2\n3\n4\n5"""


def test_for_loop_over_range_single_reference(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/for_loop_over_range_single_reference.petl", mocker, capsys) == """0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10"""


def test_for_loop_over_tuple_def_single_reference(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/for_loop_over_tuple_def_single_reference.petl", mocker, capsys) == """a\n1\nfalse"""


#def test_iterate_dict(mocker, capsys):
    #assert get_petl_program_stdout(f"{directory_prefix}/iterate_dict.petl", mocker, capsys) == """1\n2"""
