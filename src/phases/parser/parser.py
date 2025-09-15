from typing import Set

from src.builtins.builtin_definitions import Builtin
from src.builtins.builtins import get_builtin
from src.phases.interpreter.definitions.types import *
from src.phases.lexer.definitions.delimiter import Delimiter
from src.phases.lexer.definitions.keyword_petl import Keyword
from src.phases.parser.defintions.expression import *
from src.phases.phase import PetlPhase


class Parser(PetlPhase):
    def __init__(self, debug=False):
        self.logger.__init__(debug)
        self.tokens = []
        self.last_token = None
        self.tokens_length = 0
        self.current_token_index = 0
        self.dummy_count = 0
        self.aliases: dict[str, PetlType] = {}
        self.builtins: Set[Builtin] = set()

    def error(self, text: str, token: Optional[Token] = None):
        file_position_str: str = "\n" + token.file_position.to_string() if token else ""
        self.logger.error(f"{text}{file_position_str}")

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
        if token:
            token_as_operator: Optional[Operator] = token.to_operator()
            if token_as_operator:
                return token_as_operator.is_binary(min)
        return False

    def match(self, against: Union[Delimiter, Keyword], optional=True) -> bool:
        token = self.current_token()

        if not token:
            if not optional:
                self.error(f"Expected {against}, found end-of-file while parsing")
            return False

        matched = token.token_value == against

        if not matched and not optional:
            self.error(f"Expected {against}, got {token.token_value}", token)
            self.advance()
        elif not matched and not optional and token and token == self.last_token:
            self.error("Attempted to match same token twice", token)
            self.advance()
        elif matched:
            self.advance()

        return matched

    def match_ident(self, optional=False) -> Optional[str]:
        token = self.current_token()
        if token.token_type == Token.TokenType.IDENT:
            self.advance()
            self.last_token = token
            return token.token_value
        elif token == self.last_token:
            self.error("Attempted to match same token twice", token)
            self.advance()
            return None
        else:
            if not optional:
                self.error(f"Expected identifier, got {token.token_value}", token)
            return None

    def get_exp_literal(self, element: Expression) -> Optional[Literal]:
        if isinstance(element, LitExpression):
            literal: Literal = element.literal
            if literal.value is not None:
                return literal
        self.error(f"Expected literal value", self.current_token())
        return None

    def parse(self, tokens: List[Token]) -> Optional[Expression]:
        self.tokens = tokens
        self.tokens_length = len(tokens)
        root: Optional[Expression] = self.parse_expression()

        if root:
            self.logger.debug_block("PARSED EXPRESSION", root.to_string())

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
                    return Let(expression_type, token, [dummy_identifier], let_type, simple_exp, after_let_expression)
                else:
                    return simple_exp
        return UnknownExpression()

    def parse_let_identifier(self) -> Optional[Tuple[str, PetlType]]:
        identifier: Optional[str] = self.match_ident()

        if not identifier:
            return None

        let_type: PetlType = UnknownType()
        if self.match(Delimiter.DENOTE):
            let_type = self.parse_type()
        return identifier, let_type

    def parse_let(self) -> Optional[Let]:
        token = self.current_token()
        let_identifier: Optional[Tuple[str, PetlType]] = self.parse_let_identifier()

        if not let_identifier:
            return None

        let_identifiers: List[str] = [let_identifier[0]]
        let_types: List[PetlType] = [let_identifier[1]]
        while self.match(Delimiter.COMMA, optional=True):
            additional_identifier = self.parse_let_identifier()
            if not additional_identifier:
                return None
            let_identifiers.append(additional_identifier[0])
            let_types.append(additional_identifier[1])

        let_type = let_types[0] if len(let_types) == 1 else TupleType(let_types)

        self.match(Delimiter.ASSIGN)
        let_expression: Expression = self.parse_simple_expression()

        after_let_expression: Optional[Expression] = None
        if self.match(Delimiter.STMT_END):
            after_let_expression = self.parse_expression()
            if isinstance(after_let_expression, UnknownExpression):
                self.error(f"Valid expression required after \';\'", token)

        expression_type = after_let_expression.petl_type if after_let_expression else NoneType

        return Let(expression_type, token, let_identifiers, let_type, let_expression, after_let_expression)

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

    def parse_tuple_def_or_smp_expression(self) -> Optional[Expression]:
        token = self.current_token()

        if self.match(Delimiter.PAREN_RIGHT, optional=True):
            return LitExpression(NoneType(), token, NoneLiteral())

        first_element: Expression = self.parse_simple_expression()
        tuple_types: List[PetlType] = [first_element.petl_type]
        tuple_elements: List[Expression] = [first_element]
        while self.match(Delimiter.COMMA, optional=True):
            tuple_element: Expression = self.parse_simple_expression()
            tuple_types.append(tuple_element.petl_type)
            tuple_elements.append(tuple_element)

        if len(tuple_elements) == 1:
            return first_element
        else:
            return TupleDefinition(TupleType(tuple_types), token, tuple_elements)

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
        if operator and operator.operator_type == Operator.OperatorType.NOT:
            return Primitive(BoolType(), token, operator, left=LitExpression(BoolType(), token, BoolLiteral(False)), right=right)
        elif operator and operator.operator_type == Operator.OperatorType.MINUS:
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

            app_type = inner_application.petl_type
            if isinstance(app_type, FuncType):
                inner_application.petl_type = app_type.return_type
            return inner_application
        else:
            return UnknownExpression()

    def parse_atom(self) -> Optional[Expression]:
        token = self.current_token()
        if token.token_type == Token.TokenType.KEYWORD and \
                isinstance(token.token_value, Keyword) and \
                token.token_value.is_builtin_function():
            self.advance()
            builtin_reference: Builtin = get_builtin(token.token_value)
            self.builtins.add(builtin_reference)
            return Reference(builtin_reference.func_type, token, token.token_value)
        elif self.match(Delimiter.PAREN_LEFT, optional=True):
            simple_exp: Expression = self.parse_tuple_def_or_smp_expression()
            self.match(Delimiter.PAREN_RIGHT)
            return simple_exp
        elif token:
            identifier = self.match_ident(optional=True)
            if identifier:
                reference: Expression = Reference(UnknownType(), token, identifier=token.token_value)
                return reference
            else:
                return self.parse_literal()
        else:
            return UnknownExpression()

    def parse_literal(self) -> Optional[Expression]:
        token = self.current_token()
        if self.match(Keyword.TRUE):
            return LitExpression(BoolType(), token, BoolLiteral(True))
        elif self.match(Keyword.FALSE):
            return LitExpression(BoolType(), token, BoolLiteral(False))
        elif self.match(Keyword.NONE):
            return LitExpression(NoneType(), token, NoneLiteral())
        elif token.token_type == Token.TokenType.VALUE:
            if token.token_value.startswith('\''):
                self.advance()
                if len(token.token_value) == 3:
                    return LitExpression(CharType(), token, CharLiteral(token.token_value.replace('\'', '')))
                elif token.token_value.startswith("\'\\") and len(token.token_value) == 4:
                    return LitExpression(CharType(), token, CharLiteral(token.token_value.replace('\'', '')))
                else:
                    return LitExpression(StringType(), token, StringLiteral(token.token_value.replace('\'', '')))
            elif token.token_value.startswith("\"\"\""):
                self.advance()
                return LitExpression(StringType(), token, StringLiteral(token.token_value.replace('\"\"\"', '')))
            elif token.token_value.startswith('\"'):
                self.advance()
                return LitExpression(StringType(), token, StringLiteral(token.token_value.replace('\"', '')))
            else:
                integer_literal: Expression = LitExpression(IntType(), token, IntLiteral(int(token.token_value)))
                self.advance()
                if self.match(Delimiter.RANGE, optional=True):
                    range_start: Literal = self.get_exp_literal(integer_literal)
                    range_end: Literal = self.get_exp_literal(self.parse_literal())
                    return RangeDefinition(ListType(IntType()), token, range_start, range_end)
                else:
                    return integer_literal
        else:
            return UnknownExpression()

    def parse_branch(self) -> Optional[Branch]:
        token = self.current_token()
        predicate: Expression = self.parse_simple_expression()
        self.match(Delimiter.BRACE_LEFT, optional=False)
        if_branch: Expression = self.parse_expression()
        self.match(Delimiter.BRACE_RIGHT, optional=False)

        else_branch: Optional[Expression] = None
        if self.match(Keyword.ELSE, optional=True):
            self.match(Delimiter.BRACE_LEFT, optional=False)
            else_branch = self.parse_expression()
            self.match(Delimiter.BRACE_RIGHT, optional=False)

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

        after_for_expression: Optional[Expression] = None
        if self.match(Delimiter.STMT_END, optional=True):
            after_for_expression = self.parse_expression()

        return For(NoneType(), token, reference=element_reference, iterable=collection, body=body, after_for_expression=after_for_expression)

    def parse_collection_def(self) -> Optional[Expression]:
        token = self.current_token()
        if self.match(Delimiter.BRACKET_RIGHT, optional=True):
            return ListDefinition(ListType(UnknownType()), token, values=[])

        first_element: Expression = self.parse_simple_expression()
        if self.match(Delimiter.COMMA, optional=True):
            elements: List[Expression] = [first_element, self.parse_simple_expression()]
            while self.match(Delimiter.COMMA, optional=True):
                elements.append(self.parse_simple_expression())
            self.match(Delimiter.BRACKET_RIGHT)
            return ListDefinition(ListType(elements[0].petl_type), token, values=elements)
        elif self.match(Delimiter.DENOTE, optional=True):
            first_value: Expression = self.parse_simple_expression()
            mapping: List[Tuple[Expression, Expression]] = [(first_element, first_value)]
            while self.match(Delimiter.COMMA, optional=True):
                key: Expression = self.parse_simple_expression()
                self.match(Delimiter.DENOTE)
                value: Expression = self.parse_simple_expression()
                mapping.append((key, value))
            self.match(Delimiter.BRACKET_RIGHT)
            return DictDefinition(DictType(first_element.petl_type, first_value.petl_type), token, mapping)
        else:
            self.match(Delimiter.BRACKET_RIGHT)
            return ListDefinition(ListType(first_element.petl_type), token, values=[first_element])

    def parse_schema_def(self) -> Optional[SchemaDefinition]:
        token = self.current_token()
        self.match(Delimiter.BRACE_LEFT)
        mapping: List[Tuple[str, PetlType]] = []

        column_types: List[PetlType] = []
        while self.match(Delimiter.COMMA, optional=True) or not self.match(Delimiter.BRACE_RIGHT, optional=True):
            identifier: str = self.match_ident()
            self.match(Delimiter.DENOTE)
            column_type: PetlType = self.parse_type()
            column_types.append(column_type)
            mapping.append((identifier, column_type))
        return SchemaDefinition(SchemaType(column_types), token, mapping)

    def parse_pattern(self) -> Optional[Pattern]:
        token = self.current_token()
        if token.token_type == Token.TokenType.IDENT and not token.token_value == "_":
            self.advance()
            self.match(Delimiter.DENOTE)
            case_type: PetlType = self.parse_type()
            predicate: Optional[Expression] = None
            if self.match(Keyword.IF, optional=True):
                predicate = self.parse_simple_expression()
            return TypePattern(token.token_value, case_type, predicate)
        elif token.token_type == Token.TokenType.IDENT and token.token_value == "_":
            self.advance()
            return AnyPattern()
        elif token.token_type == Token.TokenType.VALUE:
            literal_expression: Expression = self.parse_literal()
            if isinstance(literal_expression, RangeDefinition):
                return RangePattern(literal_expression)
            elif isinstance(literal_expression, LitExpression):
                if self.match(Delimiter.PIPE, optional=True):
                    literals: List[Literal] = [self.get_exp_literal(literal_expression), self.get_exp_literal(self.parse_literal())]
                    while self.match(Delimiter.PIPE, optional=True):
                        literals.append(self.get_exp_literal(self.parse_literal()))
                    return MultiLiteralPattern(literals)
                else:
                    return LiteralPattern(self.get_exp_literal(literal_expression))

        self.error(f"Invalid pattern", token)
        return None

    def parse_case(self) -> Optional[Case]:
        self.match(Keyword.CASE)
        pattern: Pattern = self.parse_pattern()
        self.match(Delimiter.CASE_EXP)
        case_expression: Expression = self.parse_simple_expression()
        return Case(pattern, case_expression)

    def parse_match(self) -> Optional[Match]:
        token = self.current_token()
        value: Expression = self.parse_atom()
        self.match(Delimiter.BRACE_LEFT)
        cases: List[Case] = [self.parse_case()]
        while self.match(Delimiter.COMMA, optional=True):
            cases.append(self.parse_case())
        self.match(Delimiter.BRACE_RIGHT)
        match_type: PetlType = cases[0].case_expression.petl_type
        return Match(match_type, token, value, cases)

    def parse_parameter(self) -> Optional[Parameter]:
        token = self.current_token()
        identifier: str = self.match_ident()
        self.match(Delimiter.DENOTE)
        parameter_type: PetlType = self.parse_type()
        return Parameter(identifier, parameter_type, token)

    def parse_lambda(self) -> Optional[Lambda]:
        token = self.current_token()
        # TODO: Add lambda${count} name
        parameters: List[Parameter] = []
        parameter_types: List[PetlType] = []

        if not self.match(Delimiter.PIPE, optional=True):
            while self.match(Delimiter.COMMA, optional=True) or not self.match(Delimiter.PIPE, optional=True):
                parameter: Parameter = self.parse_parameter()
                parameters.append(parameter)
                parameter_types.append(parameter.parameter_type)

        self.match(Delimiter.RETURN)
        return_type: PetlType = self.parse_type()
        self.match(Delimiter.BRACE_LEFT)
        body: Expression = self.parse_expression()
        self.match(Delimiter.BRACE_RIGHT)
        lambda_type: FuncType = FuncType(parameter_types, return_type)
        return Lambda(lambda_type, token, parameters, return_type, body)

    def parse_arguments(self) -> Optional[List[Expression]]:
        arguments: List[Expression] = []
        if not self.match(Delimiter.PAREN_RIGHT, optional=True):
            arguments.append(self.parse_simple_expression())
            while self.match(Delimiter.COMMA, optional=True):
                arguments.append(self.parse_simple_expression())
            self.match(Delimiter.PAREN_RIGHT, optional=False)
        return arguments

    def parse_application(self) -> Optional[Expression]:
        token = self.current_token()
        identifier: Expression = self.parse_atom()

        if isinstance(identifier, LitExpression):
            return identifier
        else:
            if self.match(Delimiter.PAREN_LEFT, optional=True):
                arguments: List[Expression] = self.parse_arguments()
                application: Expression = Application(identifier.petl_type, token, identifier, arguments)

                while self.match(Delimiter.PAREN_LEFT, optional=True):
                    outer_arguments: List[Expression] = self.parse_arguments()
                    application = Application(UnknownType(), token, application, outer_arguments)
                return application
            else:
                return identifier

    def parse_type(self) -> Optional[PetlType]:
        token = self.current_token()
        first_type: Optional[PetlType] = None
        if self.match(Keyword.INT, optional=True):
            first_type = IntType()
        elif self.match(Keyword.BOOL, optional=True):
            first_type = BoolType()
        elif self.match(Keyword.CHAR, optional=True):
            first_type = CharType()
        elif self.match(Keyword.STRING, optional=True):
            first_type = StringType()
        elif self.match(Keyword.NONE, optional=True):
            first_type = NoneType()
        elif self.match(Keyword.UNION, optional=True):
            self.match(Delimiter.BRACKET_LEFT)
            union_types: List[PetlType] = [self.parse_type()]

            while self.match(Delimiter.COMMA, optional=True):
                union_types.append(self.parse_type())

            self.match(Delimiter.BRACKET_RIGHT)
            first_type = UnionType(union_types)
        elif self.match(Keyword.LIST, optional=True):
            self.match(Delimiter.BRACKET_LEFT)
            list_type: PetlType = self.parse_type()
            self.match(Delimiter.BRACKET_RIGHT)
            first_type = ListType(list_type)
        elif self.match(Keyword.DICT, optional=True):
            self.match(Delimiter.BRACKET_LEFT)
            key_type: PetlType = self.parse_type()
            self.match(Delimiter.DENOTE)
            value_type: PetlType = self.parse_type()
            self.match(Delimiter.BRACKET_RIGHT)
            first_type = DictType(key_type, value_type)
        elif self.match(Keyword.TUPLE, optional=True):
            self.match(Delimiter.BRACKET_LEFT)
            tuple_types: List[PetlType] = [self.parse_type()]

            while self.match(Delimiter.COMMA, optional=True):
                tuple_types.append(self.parse_type())
            self.match(Delimiter.BRACKET_RIGHT, optional=True)
            first_type = TupleType(tuple_types)
        elif self.match(Keyword.SCHEMA, optional=True):
            first_type = SchemaType()
        elif self.match(Keyword.TABLE, optional=True):
            first_type = TableType(SchemaType())
        elif self.match(Delimiter.PAREN_LEFT, optional=True):
            parameter_types: List[PetlType] = []
            if not self.match(Delimiter.PAREN_RIGHT, optional=True):
                parameter_types.append(self.parse_type())
                while self.match(Delimiter.COMMA, optional=True):
                    parameter_types.append(self.parse_type())
                self.match(Delimiter.PAREN_RIGHT)
            self.match(Delimiter.RETURN)
            return_type: PetlType = self.parse_type()
            first_type = FuncType(parameter_types, return_type)
        else:
            alias: Optional[str] = self.match_ident(optional=True)
            if alias:
                if alias in self.aliases:
                    alias_type: PetlType = self.aliases[alias]
                    return alias_type
                else:
                    self.error(f"Invalid alias \'{alias}\' provided", token)
                    self.advance()
                    return UnknownType()

        if self.match(Delimiter.RETURN, optional=True):
            return FuncType(parameter_types=[first_type], return_type=self.parse_type())
        if token and not first_type:
            self.error(f"Expected type signature but received none", token)
            return UnknownType()
        return first_type
