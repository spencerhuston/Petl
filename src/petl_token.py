from copy import copy
from enum import Enum
from typing import Union

from src.file_position import FilePosition
from src.delimiter import Delimiter
from src.petl_keyword import Keyword


class Token:
    class TokenType(Enum):
        DELIMITER = 1
        KEYWORD = 2
        VALUE = 3
        IDENT = 4

    token_type: TokenType = 0
    file_position: FilePosition
    token_value: Union[str, Keyword, Delimiter] = ""

    def __init__(self, token_type: TokenType, file_position: FilePosition, token_value: str):
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

    def to_string(self) -> str:
        return f"{self.token_type}: {self.token_value}\n{self.file_position.to_string()}"
