from src.phases.lexer.definitions.delimiter import Delimiter
from src.phases.lexer.definitions.keyword import Keyword
from src.phases.lexer.definitions.token import Token
from src.phases.parser.defintions.operator import Operator
from src.utils.file_position import FilePosition


def test_get_value_string():
    assert Token(Token.TokenType.IDENT, FilePosition(0, 0, ""), token_value="test").get_value() == "test"


def test_get_value_delimiter():
    assert Token(Token.TokenType.DELIMITER, FilePosition(0, 0, ""), token_value="->").get_value() == Delimiter(Delimiter.RETURN)


def test_get_value_keyword():
    assert Token(Token.TokenType.KEYWORD, FilePosition(0, 0, ""), token_value="println").get_value() == Keyword(Keyword.PRINTLN)


def test_to_operator():
    assert Token(Token.TokenType.DELIMITER, FilePosition(0, 0, ""), token_value="+").to_operator().OperatorType == Operator(Operator.OperatorType.PLUS).OperatorType


def test_to_operator_invalid():
    assert Token(Token.TokenType.KEYWORD, FilePosition(0, 0, ""), token_value="println").to_operator() is None


def test_to_string():
    assert Token(Token.TokenType.DELIMITER, FilePosition(0, 0, "+"), token_value="+").to_string() == """TokenType.DELIMITER: +\nLine: 1, column: 1\n+\n^"""
