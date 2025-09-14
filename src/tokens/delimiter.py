from typing import Optional

from src.semantic_defintions.operator import Operator
from src.utils.petl_enum import BaseEnum


class Delimiter(str, BaseEnum):
    DENOTE = ":",
    RETURN = "->",
    ASSIGN = "=",
    NEWLINE_SLASH = "\\",
    STMT_END = ";",
    RANGE = "..",
    PLUS = "+",
    MINUS = "-",
    MULTIPLY = "*",
    DIVIDE = "/",
    MODULUS = "%",
    GREATER_THAN = ">",
    LESS_THAN = "<",
    GREATER_THAN_EQ = ">=",
    LESS_THAN_EQ = "<=",
    EQUAL = "==",
    NOT_EQUAL = "!=",
    COLLECTION_CONCAT = "++",
    PIPE = "|",
    PAREN_LEFT = "(",
    PAREN_RIGHT = ")",
    BRACKET_LEFT = "[",
    BRACKET_RIGHT = "]",
    BRACE_LEFT = "{",
    BRACE_RIGHT = "}",
    COMMA = ",",
    CASE_EXP = "=>",
    BIRD = "|>",
    SCHEMA = "$"


def delimiter_to_operator(delim: Delimiter) -> Optional[Operator]:
    if delim == Delimiter.PLUS:
        return Operator(Operator.OperatorType.PLUS)
    elif delim == Delimiter.MINUS:
        return Operator(Operator.OperatorType.MINUS)
    elif delim == Delimiter.MULTIPLY:
        return Operator(Operator.OperatorType.MULTIPLY)
    elif delim == Delimiter.DIVIDE:
        return Operator(Operator.OperatorType.DIVIDE)
    elif delim == Delimiter.MODULUS:
        return Operator(Operator.OperatorType.MODULUS)
    elif delim == Delimiter.GREATER_THAN:
        return Operator(Operator.OperatorType.GREATER_THAN)
    elif delim == Delimiter.LESS_THAN:
        return Operator(Operator.OperatorType.LESS_THAN)
    elif delim == Delimiter.GREATER_THAN_EQ:
        return Operator(Operator.OperatorType.GREATER_THAN_EQUAL_TO)
    elif delim == Delimiter.LESS_THAN_EQ:
        return Operator(Operator.OperatorType.LESS_THAN_EQUAL_TO)
    elif delim == Delimiter.EQUAL:
        return Operator(Operator.OperatorType.EQUAL)
    elif delim == Delimiter.NOT_EQUAL:
        return Operator(Operator.OperatorType.NOT_EQUAL)
    elif delim == Delimiter.COLLECTION_CONCAT:
        return Operator(Operator.OperatorType.COLLECTION_CONCAT)
    else:
        return None
