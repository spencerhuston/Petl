from petllang.phases.parser.defintions.operator import Operator


def test_to_string():
    assert Operator(Operator.OperatorType.PLUS).to_string() == "+"


def test_is_arithmetic():
    assert Operator(Operator.OperatorType.PLUS).is_arithmetic()


def test_is_arithmetic_invalid():
    assert not Operator(Operator.OperatorType.GREATER_THAN).is_arithmetic()


def test_is_boolean():
    assert Operator(Operator.OperatorType.GREATER_THAN).is_boolean()


def test_is_boolean_invalid():
    assert not Operator(Operator.OperatorType.PLUS).is_boolean()


def test_is_collection():
    assert Operator(Operator.OperatorType.COLLECTION_CONCAT).is_collection()


def test_is_collection_invalid():
    assert not Operator(Operator.OperatorType.PLUS).is_collection()


def test_get_precedence():
    assert Operator(Operator.OperatorType.PLUS).get_precedence() == 2
    assert Operator(Operator.OperatorType.AND).get_precedence() == 0
    assert Operator(Operator.OperatorType.MULTIPLY).get_precedence() == 3
    assert Operator(Operator.OperatorType.GREATER_THAN).get_precedence() == 1


def test_is_binary():
    assert Operator(Operator.OperatorType.PLUS).is_binary(0)


def test_is_binary_invalid():
    assert not Operator(Operator.OperatorType.NOT).is_binary(0)
