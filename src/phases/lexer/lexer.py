import functools
import traceback
from copy import deepcopy
from typing import List, Optional

from src.phases.lexer.definitions.delimiter import Delimiter
from src.phases.lexer.definitions.keyword_petl import Keyword
from src.phases.lexer.definitions.raw_delimiter import RawDelimiter
from src.phases.lexer.definitions.token_petl import Token
from src.phases.phase import PetlPhase
from src.utils.file_position import FilePosition


class Lexer(PetlPhase):
    raw_text: str = ""
    tokens: List[Token] = []
    token_text: str = ""
    file_position = FilePosition()

    inside_quotes: bool = False
    inside_comment: bool = False
    skip: bool = False

    # Used for REPL to reset Lexer on sequential runs
    def __init__(self, debug=False):
        self.logger.__init__(debug)
        self.raw_text = ""
        self.tokens = []
        self.file_position = FilePosition()

        self.inside_quotes = False
        self.inside_comment = False
        self.skip = False

    def get_line_text(self, line_number: int) -> str:
        lines = self.raw_text.split('\n')
        return lines[line_number] if line_number < len(lines) else ""

    def create_file_position(self, extra=False, delim=False) -> FilePosition:
        file_position: FilePosition = deepcopy(self.file_position)
        file_position.line_text = self.get_line_text(file_position.line)
        column: int = file_position.column - ((1 if extra else 0) + (1 if delim else len(self.token_text)))
        file_position.column = 0 if column < 0 else column
        return file_position

    def update_file_position(self, character: str):
        if character == '\n':
            self.file_position.column = 0
            self.file_position.line += 1
            self.file_position.line_text = ""
        elif character == '\t':
            self.file_position.column += len("\t")
            self.file_position.line += character
        else:
            self.file_position.column += 1
            self.file_position.line_text += character

    def is_valid_character(self, character: str) -> bool:
        return self.inside_quotes or \
               character.isalnum() or \
               character.isspace() or \
               character == '#' or \
               character == '_' or \
               character == '\'' or \
               character == '\"' or \
               character in RawDelimiter

    def handle_extraneous(self, character: str):
        continue_scan: bool = True
        if character == '#' and not self.inside_quotes:
            self.inside_comment = True
        elif self.inside_comment:
            if character == '\n':
                self.inside_comment = False
        elif self.is_space(character):
            self.push_non_delim_token(extra=True)
        elif self.skip:
            self.skip = False
        else:
            continue_scan = False
        return continue_scan

    def handle_character(self, index: int, character: str):
        if character in RawDelimiter and not self.inside_quotes:
            self.push_non_delim_token(extra=True)
            delim_text = character
            if self.peek_raw_delim(index):
                self.skip = True
                delim_text += self.raw_text[index + 1]
                self.push_delim_tokens(delim_text, extra=True)
            else:
                self.push_delim_tokens(character)
        else:
            if character == '\'' or character == '\"':
                self.inside_quotes = not self.inside_quotes
            if (character == ' ' and self.inside_quotes) or not character.isspace():
                self.token_text += character

    def is_space(self, character: str) -> bool:
        if character == '\n' or character == '\r' or character == '\t':
            return True
        elif character == ' ':
            return False if self.inside_quotes else True
        else:
            return False

    def token_is_value(self) -> bool:
        return self.token_text == "true" or self.token_text == "false" or \
               self.token_text.isnumeric() or \
               (self.token_text.startswith('\"') and self.token_text.endswith('\"')) or \
               (self.token_text.startswith('\'') and self.token_text.endswith('\''))

    def peek_raw_delim(self, index: int) -> bool:
        return index < len(self.raw_text) - 1 and self.raw_text[index + 1] in RawDelimiter and not self.inside_quotes

    def push_non_delim_token(self, extra=False):
        file_position: FilePosition = self.create_file_position(extra=extra, delim=False)
        if self.token_text in Keyword:
            self.tokens.append(Token(Token.TokenType.KEYWORD, file_position, self.token_text))
        elif self.token_is_value():
            self.tokens.append(Token(Token.TokenType.VALUE, file_position, self.token_text))
        elif self.token_text.isidentifier():
            self.tokens.append(Token(Token.TokenType.IDENT, file_position, self.token_text))
        elif self.token_text:
            self.logger.error(f"Unexpected: {file_position.to_string()}")
        self.token_text = ""

    def push_delim_tokens(self, delim_text: str, extra=False):
        file_position: FilePosition = self.create_file_position(extra=extra, delim=True)
        if delim_text in Delimiter:
            self.tokens.append(Token(Token.TokenType.DELIMITER, file_position, delim_text))
        else:
            self.tokens.append(Token(Token.TokenType.DELIMITER, file_position, delim_text[0]))
            self.tokens.append(Token(Token.TokenType.DELIMITER, file_position, delim_text[1]))

    def scan(self, raw_text: str) -> Optional[List[Token]]:
        tokens: Optional[List[Token]] = None
        try:
            self.raw_text = raw_text
            for index in range(0, len(self.raw_text)):
                character = raw_text[index]
                self.update_file_position(character)

                if not self.is_valid_character(character):
                    invalid_character = character if character.isascii() else character.encode('utf-8')
                    self.logger.warn(f"Unexpected character \'{invalid_character}\': {self.create_file_position().to_string()}")
                    continue
                if self.handle_extraneous(character):
                    continue
                self.handle_character(index, character)

            # Push leftover token text
            self.push_non_delim_token()

            if not self.tokens:
                raise Exception("Invalid program, unable to parse")

            self.logger.debug_block(
                "TOKENS",
                functools.reduce(
                    lambda a, b: a + b,
                    [f"{i}\n{token.to_string()}\n\n" for i, token in enumerate(self.tokens)]
                )
            )
            tokens = self.tokens
        except Exception as scan_exception:
            self.logger.error(f"Unhandled error occurred: {scan_exception}")
            tokens = None
        finally:
            if self.logger.warnings_occurred():
                self.logger.warn(f"One or more warnings occurred")
            if self.logger.errors_occurred():
                self.logger.error(f"One or more errors occurred")

        return tokens
