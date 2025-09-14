from abc import ABC, abstractmethod
from dataclasses import dataclass


class QueryType(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass


@dataclass
class QueryUnknownType(QueryType):
    def to_string(self) -> str:
        return "unknown"


@dataclass
class QueryLiteralType(QueryType, ABC):
    def to_string(self) -> str:
        return "literal"


@dataclass
class QueryIntType(QueryLiteralType):
    def to_string(self) -> str:
        return "int"


@dataclass
class QueryBoolType(QueryLiteralType):
    def to_string(self) -> str:
        return "bool"


@dataclass
class QueryCharType(QueryLiteralType):
    def to_string(self) -> str:
        return "char"


@dataclass
class QueryStringType(QueryLiteralType):
    def to_string(self) -> str:
        return "string"


@dataclass
class QueryRangeType(QueryType):
    def to_string(self) -> str:
        return f"range"
