from abc import ABC
from dataclasses import dataclass
from pprint import pformat
from typing import Union

from src.utils.query.query_operator import QueryOperator
from src.utils.query.query_token import QueryToken
from src.utils.query.query_types import QueryType, QueryUnknownType


@dataclass
class QueryExpression(ABC):
    query_type: QueryType = QueryUnknownType()
    token: QueryToken = QueryToken()

    def to_string(self):
        return pformat(self)


@dataclass
class QueryUnknownExpression(QueryExpression):
    pass


@dataclass
class QueryLiteral(ABC):
    value: Union[int, bool, str, None] = None


@dataclass
class QueryIntLiteral(QueryLiteral):
    pass


@dataclass
class QueryBoolLiteral(QueryLiteral):
    pass


@dataclass
class QueryCharLiteral(QueryLiteral):
    pass


@dataclass
class QueryStringLiteral(QueryLiteral):
    pass


@dataclass
class QueryLitExpression(QueryExpression):
    literal: QueryLiteral = QueryLiteral()


@dataclass
class QueryPrimitive(QueryExpression):
    operator: QueryOperator = QueryOperator()
    left: QueryExpression = QueryUnknownExpression()
    right: QueryExpression = QueryUnknownExpression()


@dataclass
class QueryReference(QueryExpression):
    identifier: str = ""


@dataclass
class QueryRangeDefinition(QueryExpression):
    start: QueryLiteral = QueryLiteral()
    end: QueryLiteral = QueryLiteral()
