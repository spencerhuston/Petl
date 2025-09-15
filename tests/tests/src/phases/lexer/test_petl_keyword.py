from src.phases.lexer.definitions.keyword_petl import Keyword, keyword_to_operator
from src.phases.parser.defintions.operator import Operator


def test_is_builtin_function():
    assert Keyword.PRINTLN.is_builtin_function()


def test_is_builtin_function_invalid():
    assert not Keyword.STRING.is_builtin_function()


def test_keyword_to_operator():
    assert keyword_to_operator(Keyword.AND).OperatorType == Operator(Operator.OperatorType.AND).OperatorType
