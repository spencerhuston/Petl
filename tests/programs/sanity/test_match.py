from tests.programs.test_petl_program import get_petl_program_stdout


directory_prefix = "sanity/match"


def test_match_range(mocker, capsys):
    assert get_petl_program_stdout(f"{directory_prefix}/match_range.petl", mocker, capsys) == """5"""
