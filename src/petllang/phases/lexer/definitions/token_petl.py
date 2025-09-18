from dataclasses import dataclass, field
from enum import Enum
from typing import Union, Optional

from petllang.phases.lexer.definitions.delimiter import Delimiter, delimiter_to_operator
from petllang.phases.lexer.definitions.keyword_petl import Keyword, keyword_to_operator
from petllang.phases.parser.defintions.operator import Operator
from petllang.utils.file_position import FilePosition


@dataclass
class Token:
    class TokenType(Enum):
        UNKNOWN = 0,
        DELIMITER = 1,
        KEYWORD = 2,
        VALUE = 3,
        IDENT = 4

    token_value: Union[str, Delimiter, Keyword] = field(default_factory=str)

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
        token_value_text = self.token_value if isinstance(self.token_value, str) else self.token_value.value
        return f"{self.token_type}: {token_value_text}\n{self.file_position.to_string()}"
