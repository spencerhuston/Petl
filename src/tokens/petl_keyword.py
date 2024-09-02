from typing import Optional

from src.semantic_defintions.operator import Operator
from src.utils.petl_enum import BaseEnum


class Keyword(str, BaseEnum):
    LET = "let",
    ALIAS = "alias",
    INT = "int",
    BOOL = "bool",
    CHAR = "char",
    STRING = "string",
    NONE = "none",
    UNION = "union",
    LIST = "list",
    DICT = "dict",
    TUPLE = "tuple",
    SCHEMA = "schema",
    TABLE = "table",
    TRUE = "true",
    FALSE = "false",
    AND = "and",
    OR = "or",
    NOT = "not",
    IF = "if",
    ELSE = "else",
    FOR = "for",
    IN = "in",
    MATCH = "match",
    CASE = "case",
    READLN = "readln",
    PRINT = "print",
    PRINTLN = "println",
    MAP = "map",
    FILTER = "filter",
    ZIP = "zip",
    FOLDL = "foldl",
    FOLDR = "foldr",
    SLICE = "slice",
    SUBSTR = "substr",
    LEN = "len",
    TYPE = "type",
    TOSTR = "toStr",
    TOINT = "toInt",
    CREATETABLE = "createTable",
    READCSV = "readCsv",
    WRITECSV = "writeCsv",
    JOIN = "join",
    WITH = "with",
    WHERE = "where",
    SELECT = "select",
    DROP = "drop",
    COLUMN = "column",
    COLLECT = "collect",
    COUNT = "count"


def keyword_to_operator(keyword: Keyword) -> Optional[Operator]:
    if keyword == Keyword.NOT:
        return Operator(Operator.OperatorType.NOT)
    elif keyword == Keyword.AND:
        return Operator(Operator.OperatorType.AND)
    elif keyword == Keyword.OR:
        return Operator(Operator.OperatorType.OR)
    else:
        return None


def is_builtin_function(value: str) -> bool:
    return value == Keyword.READLN or \
           value == Keyword.PRINT or \
           value == Keyword.PRINTLN or \
           value == Keyword.MAP or \
           value == Keyword.FILTER or \
           value == Keyword.ZIP or \
           value == Keyword.FOLDL or \
           value == Keyword.FOLDR or \
           value == Keyword.SLICE or \
           value == Keyword.SUBSTR or \
           value == Keyword.LEN or \
           value == Keyword.TYPE or \
           value == Keyword.TOSTR or \
           value == Keyword.TOINT or \
           value == Keyword.CREATETABLE or \
           value == Keyword.READCSV or \
           value == Keyword.WRITECSV or \
           value == Keyword.JOIN or \
           value == Keyword.WITH or \
           value == Keyword.WHERE or \
           value == Keyword.SELECT or \
           value == Keyword.DROP or \
           value == Keyword.COLUMN or \
           value == Keyword.COLLECT or \
           value == Keyword.COUNT
