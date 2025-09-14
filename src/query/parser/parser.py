from typing import Optional, Union, List

from src.query.interpreter.types import QueryUnknownType, QueryBoolType, QueryIntType, QueryType, QueryCharType, \
    QueryStringType
from src.query.lexer.token import QueryToken, QueryDelimiter, QueryKeyword
from src.query.parser.expression import QueryExpression, QueryLitExpression, QueryLiteral, QueryPrimitive, \
    QueryBoolLiteral, QueryIntLiteral, QueryReference, QueryStringLiteral, QueryCharLiteral, QueryRangeDefinition, \
    QueryUnknownExpression
from src.query.parser.operator import QueryOperator


class QueryParser:
    def __init__(self):
        self.tokens = []
        self.tokens_length = 0
        self.current_token_index = 0

    def current_token(self) -> Optional[QueryToken]:
        if self.current_token_index >= self.tokens_length:
            return None
        else:
            return self.tokens[self.current_token_index]

    def advance(self):
        self.current_token_index += 1

    def is_binary_operator(self, min: int) -> bool:
        token = self.current_token()
        if token:
            token_as_operator: Optional[QueryOperator] = token.to_operator()
            if token_as_operator:
                return token_as_operator.is_binary(min)
        return False

    def match(self, against: Union[QueryDelimiter, QueryKeyword], optional=True) -> bool:
        token = self.current_token()
        if not token:
            if not optional:
                raise Exception(f"Expected {against}, found end-of-file while parsing")
            return False

        matched = token.token_value == against

        if not matched and not optional:
            raise Exception(f"Expected {against}, got {token.token_value}")
        elif matched:
            self.advance()

        return matched

    def match_ident(self, optional=False) -> Optional[str]:
        token = self.current_token()
        if token.token_type == QueryToken.QueryTokenType.IDENT:
            self.advance()
            return token.token_value
        else:
            if not optional:
                raise Exception(f"Expected identifier, got {token.token_value}")
            return None

    def get_exp_literal(self, element: QueryExpression) -> Optional[QueryLiteral]:
        if isinstance(element, QueryLitExpression):
            literal: QueryLiteral = element.literal
            if literal.value is not None:
                return literal
        raise Exception(f"Expected literal value", self.current_token())

    def parse(self, tokens: List[QueryToken]) -> Optional[QueryExpression]:
        self.tokens = tokens
        self.tokens_length = len(tokens)
        return self.parse_simple_expression()

    def parse_simple_expression(self) -> Optional[QueryExpression]:
        if self.match(QueryDelimiter.PAREN_LEFT, optional=True):
            return self.parse_simple_expression()
        elif self.current_token():
            return self.parse_utight_with_min(0)
        else:
            return QueryUnknownExpression()

    def parse_utight_with_min(self, min: int) -> Optional[QueryExpression]:
        left: QueryExpression = self.parse_utight()
        while self.is_binary_operator(min):
            operator: QueryOperator = self.current_token().to_operator()
            temp_min: int = operator.get_precedence() + 1
            self.advance()
            right: QueryExpression = self.parse_utight_with_min(temp_min)
            operator_type: QueryType = QueryUnknownType() # TODO: get operator type here
            left = QueryPrimitive(operator_type, operator, left, right)
        return left

    def parse_utight(self) -> Optional[QueryExpression]:
        operator: Optional[QueryOperator] = None
        if self.match(QueryKeyword.NOT, optional=True):
            operator = QueryOperator(QueryOperator.QueryOperatorType.NOT)
        elif self.match(QueryDelimiter.MINUS, optional=True):
            operator = QueryOperator(QueryOperator.QueryOperatorType.MINUS)

        right: QueryExpression = self.parse_tight()
        if operator and operator.operator_type == QueryOperator.QueryOperatorType.NOT:
            return QueryPrimitive(QueryBoolType(), operator, left=QueryLitExpression(QueryBoolType(), QueryBoolLiteral(False)), right=right)
        elif operator and operator.operator_type == QueryOperator.QueryOperatorType.MINUS:
            return QueryPrimitive(QueryIntType(), operator, left=QueryLitExpression(QueryIntType(), QueryIntLiteral(0)), right=right)
        else:
            return right

    def parse_tight(self) -> Optional[QueryExpression]:
        token = self.current_token()
        if self.match(QueryDelimiter.PAREN_LEFT, optional=True):
            body: QueryExpression = self.parse_simple_expression()
            self.match(QueryDelimiter.PAREN_RIGHT)
            return body
        elif token:
            return self.parse_atom()
        else:
            return QueryUnknownExpression()

    def parse_atom(self) -> Optional[QueryExpression]:
        token = self.current_token()
        if self.match(QueryDelimiter.PAREN_LEFT, optional=True):
            self.advance()
            simple_exp: QueryExpression = self.parse_simple_expression()
            self.match(QueryDelimiter.PAREN_RIGHT)
            return simple_exp
        elif token:
            identifier = self.match_ident(optional=True)
            if identifier:
                reference: QueryExpression = QueryReference(QueryUnknownType(), identifier=token.token_value)
                return reference
            else:
                return self.parse_literal()
        else:
            return QueryUnknownExpression()

    def parse_literal(self) -> Optional[QueryExpression]:
        token = self.current_token()
        if self.match(QueryKeyword.TRUE):
            return QueryLitExpression(QueryBoolType(), QueryBoolLiteral(True))
        elif self.match(QueryKeyword.FALSE):
            return QueryLitExpression(QueryBoolType(), QueryBoolLiteral(False))
        elif token.token_type == QueryToken.QueryTokenType.VALUE:
            if token.token_value.startswith('\''):
                self.advance()
                if len(token.token_value) == 3:
                    return QueryLitExpression(QueryCharType(), QueryCharLiteral(token.token_value.replace('\'', '')))
                elif token.token_value.startswith("\'\\") and len(token.token_value) == 4:
                    return QueryLitExpression(QueryCharType(), QueryCharLiteral(token.token_value.replace('\'', '')))
                else:
                    return QueryLitExpression(QueryStringType(), QueryStringLiteral(token.token_value.replace('\'', '')))
            elif token.token_value.startswith('\"'):
                self.advance()
                return QueryLitExpression(QueryStringType(), QueryStringLiteral(token.token_value.replace('\"', '')))
            else:
                integer_literal: QueryExpression = QueryLitExpression(QueryIntType(), QueryIntLiteral(int(token.token_value)))
                self.advance()
                if self.match(QueryDelimiter.RANGE, optional=True):
                    range_start: QueryLiteral = self.get_exp_literal(integer_literal)
                    range_end: QueryLiteral = self.get_exp_literal(self.parse_literal())
                    return QueryRangeDefinition(QueryIntType(), range_start, range_end)
                else:
                    return integer_literal
        else:
            return QueryUnknownExpression()
