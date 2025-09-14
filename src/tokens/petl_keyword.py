from typing import Optional

from src.semantic_defintions.operator import Operator
from src.utils.petl_enum import BaseEnum


class Keyword(str, BaseEnum):
    # literal types
    INT = "int",
    BOOL = "bool",
    CHAR = "char",
    STRING = "string",
    NONE = "none",
    # end literal types
    ALIAS = "alias",
    UNION = "union",
    LIST = "list",
    DICT = "dict",
    TUPLE = "tuple",
    SCHEMA = "schema",
    TABLE = "table",
    # literal values
    TRUE = "true",
    FALSE = "false",
    # structural expressions
    LET = "let",
    IF = "if",
    ELSE = "else",
    FOR = "for",
    IN = "in",
    MATCH = "match",
    CASE = "case",
    # logical
    AND = "and",
    OR = "or",
    NOT = "not",
    # -----builtins-----
    # IO
    READLN = "readln",
    PRINT = "print",
    PRINTLN = "println",
    # Functional
    MAP = "map",
    FILTER = "filter",
    FOLDL = "foldl",
    FOLDR = "foldr",
    # Iterable
    ZIP = "zip",
    LEN = "len",
    ISEMPTY = "isEmpty",
    # List
    INSERT = "insert",
    REMOVE = "remove",
    REPLACE = "replace",
    FRONT = "front",
    BACK = "back",
    HEAD = "head",
    TAIL = "tail",
    SLICE = "slice",
    CONTAINS = "contains",
    FIND = "find",
    FILL = "fill",
    REVERSE = "reverse",
    SET = "set",
    INTERSECT = "intersect",
    # String
    SUBSTR = "substr",
    TOSTR = "toStr",
    TOUPPER = "toUpper",
    TOLOWER = "toLower",
    STARTSWITH = "startsWith",
    ENDSWITH = "endsWith",
    # Integer
    TOINT = "toInt",
    SUM = "sum",
    PRODUCT = "product",
    MAX = "max",
    MIN = "min",
    SORT = "sort",
    # Table
    CREATETABLE = "createTable",
    READCSV = "readCsv",
    WRITECSV = "writeCsv",
    JOIN = "join",
    WITH = "with",
    SELECT = "select",
    DROP = "drop",
    COLUMNS = "columns",
    COLUMN = "column",
    COLLECT = "collect",
    COUNT = "count"
    # Miscellaneous
    TYPE = "type",
    RAND = "rand"

    def is_builtin_function(self) -> bool:
        return self == self.READLN or \
                self == self.PRINT or \
                self == self.PRINTLN or \
                self == self.MAP or \
                self == self.FILTER or \
                self == self.FOLDL or \
                self == self.FOLDR or \
                self == self.ZIP or \
                self == self.LEN or \
                self == self.ISEMPTY or \
                self == self.INSERT or \
                self == self.REMOVE or \
                self == self.REPLACE or \
                self == self.FRONT or \
                self == self.BACK or \
                self == self.HEAD or \
                self == self.TAIL or \
                self == self.SLICE or \
                self == self.CONTAINS or \
                self == self.FIND or \
                self == self.FILL or \
                self == self.REVERSE or \
                self == self.SET or \
                self == self.INTERSECT or \
                self == self.SUBSTR or \
                self == self.TOSTR or \
                self == self.TOUPPER or \
                self == self.TOLOWER or \
                self == self.STARTSWITH or \
                self == self.ENDSWITH or \
                self == self.TOINT or \
                self == self.SUM or \
                self == self.PRODUCT or \
                self == self.MAX or \
                self == self.MIN or \
                self == self.SORT or \
                self == self.CREATETABLE or \
                self == self.READCSV or \
                self == self.WRITECSV or \
                self == self.JOIN or \
                self == self.WITH or \
                self == self.SELECT or \
                self == self.DROP or \
                self == self.COLUMNS or \
                self == self.COLUMN or \
                self == self.COLLECT or \
                self == self.COUNT or \
                self == self.TYPE or \
                self == self.RAND


def keyword_to_operator(keyword: Keyword) -> Optional[Operator]:
    if keyword == Keyword.NOT:
        return Operator(Operator.OperatorType.NOT)
    elif keyword == Keyword.AND:
        return Operator(Operator.OperatorType.AND)
    elif keyword == Keyword.OR:
        return Operator(Operator.OperatorType.OR)
    else:
        return None
