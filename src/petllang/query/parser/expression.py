from abc import ABC
from dataclasses import dataclass, field
from pprint import pformat
from typing import Union

from petllang.query.interpreter.types import QueryType, QueryUnknownType
from petllang.query.parser.operator import QueryOperator


@dataclass
class QueryExpression(ABC):
    query_type: QueryType = field(default_factory=QueryUnknownType)

    def to_string(self):
        return pformat(self)


@dataclass
class QueryUnknownExpression(QueryExpression):
    pass


@dataclass
class QueryLiteral(ABC):
    value: Union[int, bool, str, None] = field(default_factory=str)


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
    literal: QueryLiteral = field(default_factory=QueryLiteral)


@dataclass
class QueryPrimitive(QueryExpression):
    operator: QueryOperator = field(default_factory=QueryOperator)
    left: QueryExpression = field(default_factory=QueryUnknownExpression)
    right: QueryExpression = field(default_factory=QueryUnknownExpression)


@dataclass
class QueryReference(QueryExpression):
    identifier: str = field(default_factory=str)


@dataclass
class QueryRangeDefinition(QueryExpression):
    start: QueryLiteral = field(default_factory=QueryLiteral)
    end: QueryLiteral = field(default_factory=QueryLiteral)
