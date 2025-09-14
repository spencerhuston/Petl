from typing import List

from src.utils.query.query_token import QueryRawDelimiter, QueryToken, QueryKeyword, QueryDelimiter


class QueryLexer:
    tokens = []
    text = ""
    token_text = ""

    inside_quotes: bool = False
    inside_comment: bool = False
    skip: bool = False

    def is_valid_character(self, character: str) -> bool:
        return self.inside_quotes or \
               character.isalnum() or \
               character.isspace() or \
               character == '.' or \
               character == '_' or \
               character == '\'' or \
               character == '\"' or \
               character in QueryRawDelimiter

    def handle_extraneous(self, character: str):
        continue_scan: bool = True
        if self.is_space(character):
            self.push_non_delim_token()
        elif self.skip:
            self.skip = False
        else:
            continue_scan = False
        return continue_scan

    def handle_character(self, index: int, character: str):
        if character in QueryRawDelimiter and not self.inside_quotes:
            self.push_non_delim_token()
            delim_text = character
            if self.peek_raw_delim(index):
                self.skip = True
                delim_text += self.text[index + 1]
                self.push_delim_tokens(delim_text)
            else:
                self.push_delim_tokens(character)
        else:
            if character == '\'' or character == '\"':
                self.inside_quotes = not self.inside_quotes
            if (character == ' ' and self.inside_quotes) or not character.isspace():
                self.token_text += character

    def is_space(self, character: str) -> bool:
        if character == ' ':
            return False if self.inside_quotes else True
        else:
            return False

    def token_is_value(self) -> bool:
        return self.token_text == "true" or self.token_text == "false" or \
               self.token_text.isnumeric() or \
               (self.token_text.startswith('\"') and self.token_text.endswith('\"')) or \
               (self.token_text.startswith('\'') and self.token_text.endswith('\''))

    def peek_raw_delim(self, index: int) -> bool:
        return index < len(self.text) - 1 and self.text[index + 1] in QueryRawDelimiter and not self.inside_quotes

    def push_non_delim_token(self):
        if self.token_text in QueryKeyword:
            self.tokens.append(QueryToken(QueryToken.QueryTokenType.KEYWORD, self.token_text))
        elif self.token_is_value():
            self.tokens.append(QueryToken(QueryToken.QueryTokenType.VALUE, self.token_text))
        elif self.token_text.replace(".", "").isidentifier():
            self.tokens.append(QueryToken(QueryToken.QueryTokenType.IDENT, self.token_text))
        elif self.token_text:
            raise Exception(f"Invalid query")
        self.token_text = ""

    def push_delim_tokens(self, delim_text: str):
        if delim_text in QueryDelimiter:
            self.tokens.append(QueryToken(QueryToken.QueryTokenType.DELIMITER, delim_text))
        else:
            self.tokens.append(QueryToken(QueryToken.QueryTokenType.DELIMITER, delim_text[0]))
            self.tokens.append(QueryToken(QueryToken.QueryTokenType.DELIMITER, delim_text[1]))

    def scan(self, text: str) -> List[QueryToken]:
        self.text = text
        for index in range(0, len(text)):
            character = text[index]
            if not self.is_valid_character(character):
                raise Exception(f"Unexpected character in query \'{character}\'")
            if self.handle_extraneous(character):
                continue
            self.handle_character(index, character)
        # Push leftover token text
        self.push_non_delim_token()
        return self.tokens
