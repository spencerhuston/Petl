from src.tokens.delimiter import Delimiter, delimiter_to_operator
from src.semantic_defintions.operator import Operator


def test_delimiter_to_operator():
    assert delimiter_to_operator(Delimiter.PLUS).OperatorType == Operator(Operator.OperatorType.PLUS).OperatorType


def test_delimiter_to_operator_invalid():
    assert delimiter_to_operator(Delimiter.DENOTE) is None
