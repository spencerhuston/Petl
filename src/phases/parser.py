from src.phases.petl_phase import PetlPhase
from src.semantic_defintions.petl_expression import *
from src.semantic_defintions.petl_types import PetlType
from src.tokens.petl_token import Token
from src.tokens.delimiter import Delimiter
from src.tokens.petl_keyword import Keyword


class Parser(PetlPhase):
    tokens: List[Token] = []
    tokens_length: int = 0
    current_token_index: int = 0
    dummy_count: int = 0

    def __init__(self, debug=False):
        self.logger.__init__(debug)
        self.tokens = []
        self.tokens_length = 0
        self.current_token_index = 0
        self.dummy_count = 0

    def current_token(self) -> Optional[Token]:
        if self.current_token_index >= self.tokens_length:
            return None
        else:
            return self.tokens[self.current_token_index]

    def advance(self):
        self.current_token_index += 1

    def dummy(self) -> str:
        dummy_str = f"dummy${self.dummy_count}"
        self.dummy_count += 1
        return dummy_str

    def match(self, against: Union[Delimiter, Keyword], optional=True) -> bool:
        token = self.current_token()
        matched = token.token_value == against

        if not matched and not optional:
            self.logger.error(f"Expected {against}, got {token.token_value}\n{token.file_position.to_string()}")
            self.advance()
        elif matched:
            self.advance()

        return matched

    def match_ident(self) -> Optional[str]:
        token = self.current_token()
        if token.token_type == Token.TokenType.IDENT:
            return token.token_value
        else:
            self.logger.error(f"Expected identifier, got {token.token_value}\n{token.file_position.to_string()}")
            return None

    def parse(self, tokens: List[Token]) -> Optional[Expression]:
        self.tokens = tokens
        self.tokens_length = len(tokens)
        root: Optional[Expression] = self.parse_expression()
        return root

    def parse_expression(self) -> Optional[Expression]:
        if self.current_token():
            if self.match(Keyword.LET):
                return self.parse_let()
            else:
                simple_exp: Expression = self.parse_simple_expression()
                if self.match(Delimiter.STMT_END, optional=True):
                    token = simple_exp.token
                    dummy_identifier = self.dummy()
                    let_type: PetlType = simple_exp.petl_type
                    after_let_expression: Expression = self.parse_expression()
                    expression_type: PetlType = after_let_expression.petl_type
                    return Let(expression_type, token, dummy_identifier, let_type, simple_exp, after_let_expression)
        return UnknownExpression() # TODO: Change?

    def parse_let(self) -> Optional[Let]:
        token = self.current_token()
        identifier: Optional[str] = self.match_ident()

        if not identifier:
            return None

        let_type: PetlType = UnknownType()
        if self.match(Delimiter.DENOTE):
            let_type = self.parse_type()

        self.match(Delimiter.ASSIGN)
        let_expression: Expression = self.parse_simple_expression()

        after_let_expression: Optional[Expression] = None
        if self.match(Delimiter.STMT_END):
            after_let_expression = self.parse_expression()
        expression_type = after_let_expression.petl_type

        return Let(expression_type, token, identifier, let_type, let_expression, after_let_expression)

    def parse_simple_expression(self) -> Optional[Let]:
        pass

    def parse_type(self) -> Optional[PetlType]:
        pass
