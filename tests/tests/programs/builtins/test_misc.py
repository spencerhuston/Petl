from tests.tests.programs.test_petl_program import get_petl_program_stdout


directory_prefix = "resources/examples/programs/builtins/misc"


def test_rand(mocker, capsys):
    rand_result = int(get_petl_program_stdout(f"{directory_prefix}/rand.petl", mocker, capsys))
    assert 0 <= rand_result <= 100


def test_type(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/type.petl", mocker, capsys) == """tuple[dict[char:list[int]], bool]"""
