from enum import Enum
from typing import Union, Optional

from src.utils.petl_enum import BaseEnum
from src.utils.query.query_operator import QueryOperator


class QueryRawDelimiter(str, BaseEnum):
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
    EXCLAMATION = "!",
    TILDE = "~"


class QueryDelimiter(str, BaseEnum):
    RANGE = "~",
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
    PAREN_RIGHT = ")"


def delimiter_to_operator(delim: QueryDelimiter) -> Optional[QueryOperator]:
    if delim == QueryDelimiter.PLUS:
        return QueryOperator(QueryOperator.QueryOperatorType.PLUS)
    elif delim == QueryDelimiter.MINUS:
        return QueryOperator(QueryOperator.QueryOperatorType.MINUS)
    elif delim == QueryDelimiter.MULTIPLY:
        return QueryOperator(QueryOperator.QueryOperatorType.MULTIPLY)
    elif delim == QueryDelimiter.DIVIDE:
        return QueryOperator(QueryOperator.QueryOperatorType.DIVIDE)
    elif delim == QueryDelimiter.MODULUS:
        return QueryOperator(QueryOperator.QueryOperatorType.MODULUS)
    elif delim == QueryDelimiter.GREATER_THAN:
        return QueryOperator(QueryOperator.QueryOperatorType.GREATER_THAN)
    elif delim == QueryDelimiter.LESS_THAN:
        return QueryOperator(QueryOperator.QueryOperatorType.LESS_THAN)
    elif delim == QueryDelimiter.GREATER_THAN_EQ:
        return QueryOperator(QueryOperator.QueryOperatorType.GREATER_THAN_EQUAL_TO)
    elif delim == QueryDelimiter.LESS_THAN_EQ:
        return QueryOperator(QueryOperator.QueryOperatorType.LESS_THAN_EQUAL_TO)
    elif delim == QueryDelimiter.EQUAL:
        return QueryOperator(QueryOperator.QueryOperatorType.EQUAL)
    elif delim == QueryDelimiter.NOT_EQUAL:
        return QueryOperator(QueryOperator.QueryOperatorType.NOT_EQUAL)
    else:
        return None


class QueryKeyword(str, BaseEnum):
    TRUE = "true",
    FALSE = "false",
    AND = "and",
    OR = "or",
    NOT = "not",
    IN = "in"


def keyword_to_operator(keyword: QueryKeyword) -> Optional[QueryOperator]:
    if keyword == QueryKeyword.NOT:
        return QueryOperator(QueryOperator.QueryOperatorType.NOT)
    elif keyword == QueryKeyword.AND:
        return QueryOperator(QueryOperator.QueryOperatorType.AND)
    elif keyword == QueryKeyword.OR:
        return QueryOperator(QueryOperator.QueryOperatorType.OR)
    elif keyword == QueryKeyword.IN:
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

    token_value: Union[str, QueryDelimiter, QueryKeyword] = ""

    def __init__(self, token_type=QueryTokenType.UNKNOWN, token_value=""):
        self.token_type = token_type

        if self.token_type is self.QueryTokenType.KEYWORD:
            self.token_value = QueryKeyword(token_value)
        elif self.token_type is self.QueryTokenType.DELIMITER:
            self.token_value = QueryDelimiter(token_value)
        else:
            self.token_value = token_value

    def get_value(self) -> Union[str, QueryKeyword, QueryDelimiter]:
        return self.token_value

    def to_operator(self) -> Optional[QueryOperator]:
        if self.token_type == QueryToken.QueryTokenType.DELIMITER:
            return delimiter_to_operator(self.token_value)
        elif self.token_type == QueryToken.QueryTokenType.KEYWORD:
            return keyword_to_operator(self.token_value)
        else:
            return None
