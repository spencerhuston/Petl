from petllang.execution.run_cli import run_cli


def get_petl_program_stdout(petl_file_path: str, mocker, capsys) -> str:
    mocker.patch("petllang.execution.run_cli.parse_arguments", return_value={"file": f"{petl_file_path}", "debug": False})
    run_cli()
    return str(capsys.readouterr().out).strip()
