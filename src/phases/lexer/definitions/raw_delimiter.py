from src.utils.petl_enum import PetlBaseEnum


class RawDelimiter(str, PetlBaseEnum):
    DENOTE = ":",
    ASSIGN = "=",
    NEWLINE_SLASH = "\\",
    STMT_END = ";",
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
    SCHEMA = "$",
    EXCLAMATION = "!",
    TILDE = "~"
