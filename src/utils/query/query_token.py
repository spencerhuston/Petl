from enum import Enum
from typing import Union, Optional

from src.utils.petl_enum import BaseEnum
from src.utils.query.query_operator import QueryOperator


class RawDelimiter(str, BaseEnum):
    DENOTE = ":",
    ASSIGN = "=",
    PLUS = "+",
    MINUS = "-",
    MULTIPLY = "*",
    DIVIDE = "/",
    MODULUS = "%",
    GREATER_THAN = ">",
    LESS_THAN = "<",
    PAREN_LEFT = "(",
    PAREN_RIGHT = ")",
    EXCLAMATION = "!"


class Delimiter(str, BaseEnum):
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
    PAREN_LEFT = "(",
    PAREN_RIGHT= ")"


def delimiter_to_operator(delim: Delimiter) -> Optional[QueryOperator]:
    if delim == Delimiter.PLUS:
        return QueryOperator(QueryOperator.QueryOperatorType.PLUS)
    elif delim == Delimiter.MINUS:
        return QueryOperator(QueryOperator.QueryOperatorType.MINUS)
    elif delim == Delimiter.MULTIPLY:
        return QueryOperator(QueryOperator.QueryOperatorType.MULTIPLY)
    elif delim == Delimiter.DIVIDE:
        return QueryOperator(QueryOperator.QueryOperatorType.DIVIDE)
    elif delim == Delimiter.MODULUS:
        return QueryOperator(QueryOperator.QueryOperatorType.MODULUS)
    elif delim == Delimiter.GREATER_THAN:
        return QueryOperator(QueryOperator.QueryOperatorType.GREATER_THAN)
    elif delim == Delimiter.LESS_THAN:
        return QueryOperator(QueryOperator.QueryOperatorType.LESS_THAN)
    elif delim == Delimiter.GREATER_THAN_EQ:
        return QueryOperator(QueryOperator.QueryOperatorType.GREATER_THAN_EQUAL_TO)
    elif delim == Delimiter.LESS_THAN_EQ:
        return QueryOperator(QueryOperator.QueryOperatorType.LESS_THAN_EQUAL_TO)
    elif delim == Delimiter.EQUAL:
        return QueryOperator(QueryOperator.QueryOperatorType.EQUAL)
    elif delim == Delimiter.NOT_EQUAL:
        return QueryOperator(QueryOperator.QueryOperatorType.NOT_EQUAL)
    else:
        return None


class Keyword(str, BaseEnum):
    TRUE = "true",
    FALSE = "false",
    AND = "and",
    OR = "or",
    NOT = "not",
    IN = "in"


def keyword_to_operator(keyword: Keyword) -> Optional[QueryOperator]:
    if keyword == Keyword.NOT:
        return QueryOperator(QueryOperator.QueryOperatorType.NOT)
    elif keyword == Keyword.AND:
        return QueryOperator(QueryOperator.QueryOperatorType.AND)
    elif keyword == Keyword.OR:
        return QueryOperator(QueryOperator.QueryOperatorType.OR)
    elif keyword == Keyword.IN:
        return QueryOperator(QueryOperator.QueryOperatorType.IN)
    else:
        return None


class QueryToken:
    class QueryTokenType(Enum):
        UNKNOWN = 0,
        DELIMITER = 1,
        KEYWORD = 2,
        VALUE = 3,
        IDENT = 4

    token_value: Union[str, Delimiter, Keyword] = ""

    def __init__(self, token_type=QueryTokenType.UNKNOWN, token_value=""):
        self.token_type = token_type

        if self.token_type is self.QueryTokenType.KEYWORD:
            self.token_value = Keyword(token_value)
        elif self.token_type is self.QueryTokenType.DELIMITER:
            self.token_value = Delimiter(token_value)
        else:
            self.token_value = token_value

    def get_value(self) -> Union[str, Keyword, Delimiter]:
        return self.token_value

    def to_operator(self) -> Optional[QueryOperator]:
        if self.token_type == QueryToken.QueryTokenType.DELIMITER:
            return delimiter_to_operator(self.token_value)
        elif self.token_type == QueryToken.QueryTokenType.KEYWORD:
            return keyword_to_operator(self.token_value)
        else:
            return None
