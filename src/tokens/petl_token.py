from dataclasses import dataclass
from enum import Enum
from typing import Union, Optional

from src.semantic_defintions.operator import Operator
from src.tokens.delimiter import Delimiter, delimiter_to_operator
from src.tokens.petl_keyword import Keyword, keyword_to_operator
from src.utils.file_position import FilePosition


@dataclass
class Token:
    class TokenType(Enum):
        UNKNOWN = 0,
        DELIMITER = 1,
        KEYWORD = 2,
        VALUE = 3,
        IDENT = 4

    token_value: Union[str, Delimiter, Keyword] = ""

    def __init__(self, token_type=TokenType.UNKNOWN, file_position=FilePosition(), token_value=""):
        self.token_type = token_type
        self.file_position = file_position

        if self.token_type is self.TokenType.KEYWORD:
            self.token_value = Keyword(token_value)
        elif self.token_type is self.TokenType.DELIMITER:
            self.token_value = Delimiter(token_value)
        else:
            self.token_value = token_value

    def get_value(self) -> Union[str, Keyword, Delimiter]:
        return self.token_value

    def to_operator(self) -> Optional[Operator]:
        if self.token_type == Token.TokenType.DELIMITER:
            return delimiter_to_operator(self.token_value)
        elif self.token_type == Token.TokenType.KEYWORD:
            return keyword_to_operator(self.token_value)
        else:
            return None

    def to_string(self) -> str:
        return f"{self.token_type}: {self.token_value}\n{self.file_position.to_string()}"
