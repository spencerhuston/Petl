from abc import ABC, abstractmethod
from pprint import pformat

from src.query.interpreter.types import QueryType, QueryCharType, QueryBoolType, QueryIntType, QueryStringType, \
    QueryRangeType


class QueryValue(ABC):
    def __init__(self, query_type: QueryType):
        self.query_type = query_type

    @abstractmethod
    def to_string(self) -> str:
        pass

    def to_formatted_string(self) -> str:
        return pformat(self)


def values_equal(value1: QueryValue, value2: QueryValue) -> bool:
    if isinstance(value1, QueryIntValue) and isinstance(value2, QueryIntValue):
        return value1.value == value2.value
    elif isinstance(value1, QueryBoolValue) and isinstance(value2, QueryBoolValue):
        return value1.value == value2.value
    elif isinstance(value1, QueryCharValue) and isinstance(value2, QueryCharValue):
        return value1.value == value2.value
    elif isinstance(value1, QueryStringValue) and isinstance(value2, QueryStringValue):
        return value1.value == value2.value
    else:
        return False


class QueryIntValue(QueryValue):
    def __init__(self, value: int):
        QueryValue.__init__(self, QueryIntType())
        self.value: int = value

    def to_string(self) -> str:
        return str(self.value)


class QueryBoolValue(QueryValue):
    def __init__(self, value: bool):
        QueryValue.__init__(self, QueryBoolType())
        self.value: bool = value

    def to_string(self) -> str:
        return str("true" if self.value else "false")


class QueryCharValue(QueryValue):
    def __init__(self, value: str):
        QueryValue.__init__(self, QueryCharType())
        self.value: str = value

    def to_string(self) -> str:
        return self.value


class QueryStringValue(QueryValue):
    def __init__(self, value: str):
        QueryValue.__init__(self, QueryStringType())
        self.value: str = value

    def to_string(self) -> str:
        return self.value


class QueryRangeValue(QueryValue):
    def __init__(self, start_value: int, end_value: int):
        QueryValue.__init__(self, QueryRangeType())
        self.start_value: int = start_value
        self.end_value: int = end_value

    def to_string(self) -> str:
        return f"{self.start_value}~{self.end_value}"
