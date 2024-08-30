from src.phases.petl_phase import PetlPhase
from src.semantic_defintions.petl_expression import *
from src.semantic_defintions.petl_types import *
from src.tokens.petl_token import Token
from src.tokens.delimiter import Delimiter
from src.tokens.petl_keyword import Keyword, is_builtin_function


class Parser(PetlPhase):
    def __init__(self, debug=False):
        self.logger.__init__(debug)
        self.tokens = []
        self.tokens_length = 0
        self.current_token_index = 0
        self.dummy_count = 0
        self.aliases: dict[str, PetlType] = {}

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

    def is_binary_operator(self, min: int) -> bool:
        token = self.current_token()
        return token and token.to_operator().is_binary(min)

    def match(self, against: Union[Delimiter, Keyword], optional=True) -> bool:
        token = self.current_token()
        matched = token.token_value == against

        if not matched and not optional:
            self.logger.error(f"Expected {against}, got {token.token_value}\n{token.file_position.to_string()}")
            self.advance()
        elif matched:
            self.advance()

        return matched

    def match_ident(self, optional=False) -> Optional[str]:
        token = self.current_token()
        if token.token_type == Token.TokenType.IDENT:
            return token.token_value
        else:
            if not optional:
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

    def parse_simple_expression(self) -> Optional[Expression]:
        if self.match(Keyword.IF, optional=True):
            return self.parse_branch()
        elif self.match(Keyword.FOR, optional=True):
            return self.parse_for()
        elif self.match(Delimiter.BRACKET_LEFT, optional=True):
            collection1: Expression = self.parse_collection_def()
            if self.match(Delimiter.COLLECTION_CONCAT, optional=True):
                collection2: Expression = self.parse_tight()
                return Primitive(
                    UnknownType(),
                    self.current_token(),
                    Operator(Operator.OperatorType.COLLECTION_CONCAT),
                    collection1,
                    collection2
                )
            else:
                return collection1
            pass
        elif self.match(Delimiter.PAREN_LEFT, optional=True):
            return self.parse_tuple_def_or_smp_expression()
        elif self.match(Delimiter.SCHEMA, optional=True):
            return self.parse_schema_def()
        elif self.match(Keyword.MATCH, optional=True):
            return self.parse_match()
        elif self.match(Delimiter.PIPE, optional=True):
            return self.parse_lambda()
        elif self.match(Keyword.ALIAS, optional=True):
            return self.parse_alias()
        elif self.current_token():
            return self.parse_utight_with_min(0)
        else:
            return UnknownExpression()

    def parse_alias(self) -> Optional[Alias]:
        token = self.current_token()
        identifier: str = self.match_ident()
        self.match(Delimiter.ASSIGN)
        alias_type: PetlType = self.parse_type()
        self.aliases[identifier] = alias_type
        after_alias_expression: Optional[Expression] = None
        if self.match(Delimiter.STMT_END, optional=True):
            after_alias_expression = self.parse_expression()
        expression_type: PetlType = after_alias_expression.petl_type
        return Alias(expression_type, token, identifier, alias_type, after_alias_expression)

    def parse_utight_with_min(self, min: int) -> Optional[Expression]:
        token = self.current_token()
        left: Expression = self.parse_utight()
        while self.is_binary_operator(min):
            operator: Operator = self.current_token().to_operator()
            temp_min: int = operator.get_precedence() + 1
            self.advance()
            right: Expression = self.parse_utight_with_min(temp_min)
            operator_type: PetlType = UnknownType() # TODO: get operator type here
            left = Primitive(operator_type, token, operator, left, right)
        return left

    def parse_utight(self) -> Optional[Expression]:
        token = self.current_token()
        operator: Optional[Operator] = None
        if self.match(Keyword.NOT, optional=True):
            operator = Operator(Operator.OperatorType.NOT)
        elif self.match(Delimiter.MINUS, optional=True):
            operator = Operator(Operator.OperatorType.MINUS)

        right: Expression = self.parse_tight()
        if operator.OperatorType == Operator.OperatorType.NOT:
            return Primitive(BoolType(), token, operator, left=LitExpression(BoolType(), token, BoolLiteral(False)), right=right)
        elif operator.OperatorType == Operator.OperatorType.MINUS:
            return Primitive(IntType(), token, operator, left=LitExpression(IntType(), token, IntLiteral(0)), right=right)
        else:
            return right

    def parse_tight(self) -> Optional[Expression]:
        token = self.current_token()
        if self.match(Delimiter.BRACKET_LEFT, optional=True):
            return self.parse_collection_def()
        elif self.match(Delimiter.BRACE_LEFT, optional=True):
            body: Expression = self.parse_expression()
            self.match(Delimiter.BRACE_RIGHT)
            return body
        elif self.match(Delimiter.PAREN_LEFT, optional=True):
            body: Expression = self.parse_simple_expression()
            self.match(Delimiter.PAREN_RIGHT)
            return body
        elif token:
            inner_application: Expression = self.parse_application()
            while self.match(Delimiter.BIRD, optional=True):
                outer_application: Expression = self.parse_application()
                if isinstance(outer_application, Application):
                    outer_application.arguments.insert(0, inner_application)
                    inner_application = outer_application
                elif isinstance(outer_application, Reference):
                    inner_application = Application(
                        outer_application.petl_type,
                        inner_application.token,
                        identifier=outer_application,
                        arguments=[inner_application]
                    )
            return inner_application
        else:
            return UnknownExpression()

    def parse_atom(self) -> Optional[Expression]:
        token = self.current_token()
        if token.token_type == Token.TokenType.KEYWORD and is_builtin_function(token.token_value):
            return Reference(UnknownType(), token, token.token_value)
        elif self.match(Delimiter.PAREN_LEFT, optional=True):
            self.advance()
            simple_exp: Expression = self.parse_tuple_def_or_smp_expression()
            self.match(Delimiter.PAREN_RIGHT)
            return simple_exp
        elif token:
            identifier = self.match_ident(optional=True)
            if identifier:
                reference: Expression = Reference(UnknownType(), token, identifier=token.token_value)
                self.advance()
                return reference
            else:
                return self.parse_literal()
        else:
            return UnknownExpression()

    def parse_literal(self) -> Optional[Expression]:
        pass

    def parse_branch(self) -> Optional[Branch]:
        token = self.current_token()
        self.match(Delimiter.PAREN_LEFT)
        predicate: Expression = self.parse_simple_expression()
        self.match(Delimiter.PAREN_RIGHT)
        self.match(Delimiter.BRACE_LEFT)
        if_branch: Expression = self.parse_expression()
        self.match(Delimiter.BRACE_RIGHT)

        else_branch: Optional[Expression] = None
        if self.match(Keyword.ELSE, optional=True):
            self.match(Delimiter.BRACE_LEFT)
            else_branch = self.parse_expression()
            self.match(Delimiter.BRACE_RIGHT)

        branch_type: PetlType = else_branch.petl_type if else_branch else NoneType()
        return Branch(branch_type, token, predicate, if_branch, else_branch)

    def parse_for(self) -> Optional[For]:
        token = self.current_token()
        element_reference: str = self.match_ident()
        self.match(Keyword.IN)
        collection: Expression = self.parse_simple_expression()
        self.match(Delimiter.BRACE_LEFT)
        body: Expression = self.parse_expression()
        self.match(Delimiter.BRACE_RIGHT)
        return For(NoneType(), token, reference=element_reference, iterable=collection, body=body)

    def parse_collection_def(self) -> Optional[For]:
        pass

    def parse_tuple_def_or_smp_expression(self) -> Optional[Expression]:
        pass

    def parse_schema_def(self) -> Optional[SchemaDefinition]:
        pass

    def parse_pattern(self) -> Optional[Pattern]:
        pass

    def parse_case(self) -> Optional[Case]:
        pass

    def parse_match(self) -> Optional[Match]:
        pass

    def parse_parameter(self) -> Optional[Parameter]:
        pass

    def parse_lambda(self) -> Optional[Lambda]:
        pass

    def parse_arguments(self) -> Optional[List[Expression]]:
        pass

    def parse_application(self) -> Optional[Expression]:
        pass

    def parse_type(self) -> Optional[PetlType]:
        pass
