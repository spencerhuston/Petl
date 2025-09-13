from src.utils.petl_enum import BaseEnum


class RawDelimiter(str, BaseEnum):
    DENOTE = ":",
    ASSIGN = "=",
    NEWLINE_SLASH = "\\",
    STMT_END = ";",
    PERIOD = ".",
    PLUS = "+",
    MINUS = "-",
    MULTIPLY = "*",
    DIVIDE = "/",
    MODULUS = "%",
    GREATER_THAN = ">",
    LESS_THAN = "<",
    PIPE = "|",
    PAREN_LEFT = "(",
    PAREN_RIGHT = ")",
    BRACKET_LEFT = "[",
    BRACKET_RIGHT = "]",
    BRACE_LEFT = "{",
    BRACE_RIGHT = "}",
    COMMNA = ",",
    SCHEMA = "$"
    EXCLAMATION = "!"
