import src.main


def get_petl_program_stdout(petl_file_path: str, mocker, capsys) -> str:
    mocker.patch("src.main.parse_arguments", return_value={"file": f"{petl_file_path}", "debug": False})
    src.main.main()
    return str(capsys.readouterr().out).strip()
