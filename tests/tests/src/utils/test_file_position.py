from src.utils.file_position import FilePosition


def test_to_string():
    fp = FilePosition(15, 8, "println(\"test\")")
    assert fp.to_string().strip() == """Line: 16, column: 9\nprintln("test")\n--------^"""
