from tests.tests.programs.test_petl_program import get_petl_program_stdout


directory_prefix = "resources/programs/builtins/list"


def test_contains(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/contains.petl", mocker, capsys) == """true\nfalse"""


def test_fill(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/fill.petl", mocker, capsys) == """[a, a, a, a, a, a, a, a, a, a]"""


def test_find(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/find.petl", mocker, capsys) == """3\n-1"""


def test_front_back_head_tail(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/front_back_head_tail.petl", mocker, capsys) == """0\n5\n[1, 2, 3, 4, 5]\n[0, 1, 2, 3, 4]"""


def test_insert(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/insert.petl", mocker, capsys) == """[1, 2, 3]\n[0, 1, 2, 3]"""


def test_intersect(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/intersect.petl", mocker, capsys) == """[1, 4, 5, 8]"""


def test_remove(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/remove.petl", mocker, capsys) == """[1, 2, 3]\n[1, 3]"""


def test_replace(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/replace.petl", mocker, capsys) == """[0, 1, 2, 3, 4, 5]\n[0, 1, 6, 3, 4, 5]"""


def test_reverse(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/reverse.petl", mocker, capsys) == """[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]\n[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]"""


def test_set(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/set.petl", mocker, capsys) == """[1, 3, 4, 6]\n[3, 6, 7, 8]\n[1, 3, 4, 6, 7, 8]"""
