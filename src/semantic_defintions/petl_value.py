from pprint import pformat
from typing import Tuple

from src.semantic_defintions.petl_expression import Expression
from src.semantic_defintions.petl_types import *


class PetlValue(ABC):
    def __init__(self, petl_type: PetlType):
        self.petl_type = petl_type

    @abstractmethod
    def to_string(self) -> str:
        pass

    def to_formatted_string(self) -> str:
        return pformat(self)


def values_equal(value1: PetlValue, value2: PetlValue) -> bool:
    if isinstance(value1, IntValue) and isinstance(value2, IntValue):
        return value1.value == value2.value
    elif isinstance(value1, BoolValue) and isinstance(value2, BoolValue):
        return value1.value == value2.value
    elif isinstance(value1, CharValue) and isinstance(value2, CharValue):
        return value1.value.replace('\'', '') == value2.value.replace('\'', '')
    elif isinstance(value1, StringValue) and isinstance(value2, StringValue):
        return value1.value.replace('\"', '') == value2.value.replace('\"', '')
    elif isinstance(value1, NoneValue) and isinstance(value2, NoneValue):
        return True
    elif isinstance(value1, ListValue) and isinstance(value2, ListValue):
        return all(map(lambda v1, v2: values_equal(v1, v2), value1.values, value2.values))
    elif isinstance(value1, TupleValue) and isinstance(value2, TupleValue):
        return all(map(lambda v1, v2: values_equal(v1, v2), value1.values, value2.values))
    elif isinstance(value1, DictValue) and isinstance(value2, DictValue):
        return all(map(lambda v1, v2: values_equal(v1[0], v2[0]) and values_equal(v1[1], v2[1]), value1.values, value2.values))
    else:
        return False


class IntValue(PetlValue):
    def __init__(self, value: int):
        PetlValue.__init__(self, IntType())
        self.value: int = value

    def to_string(self) -> str:
        return str(self.value)


class BoolValue(PetlValue):
    def __init__(self, value: bool):
        PetlValue.__init__(self, BoolType())
        self.value: bool = value

    def to_string(self) -> str:
        return str("true" if self.value else "false")


class CharValue(PetlValue):
    def __init__(self, value: str):
        PetlValue.__init__(self, CharType())
        self.value: str = value

    def to_string(self) -> str:
        return self.value.replace('\'', '')


class StringValue(PetlValue):
    def __init__(self, value: str):
        PetlValue.__init__(self, StringType())
        self.value: str = value

    def to_string(self) -> str:
        return self.value.replace('\"', '')


class NoneValue(PetlValue):
    def __init__(self):
        PetlValue.__init__(self, NoneType())
        self.value: None = None

    def to_string(self) -> str:
        return "none"


class ListValue(PetlValue):
    def __init__(self, petl_type: PetlType, values: List[PetlValue]):
        PetlValue.__init__(self, petl_type)
        self.values = values

    def to_string(self) -> str:
        elements_string: str = functools.reduce(lambda v1, v2: v1 + ", " + v2, map(lambda v: v.to_string(), self.values))
        return f"[{elements_string}]"


class TupleValue(PetlValue):
    def __init__(self, petl_type: PetlType, values: List[PetlValue]):
        PetlValue.__init__(self, petl_type)
        self.values = values

    def to_string(self) -> str:
        elements_string: str = functools.reduce(lambda v1, v2: v1 + ", " + v2, map(lambda v: v.to_string(), self.values))
        return f"({elements_string})"


class DictValue(PetlValue):
    def __init__(self, petl_type: PetlType, values: List[Tuple[PetlValue, PetlValue]]):
        PetlValue.__init__(self, petl_type)
        self.values = values

    def to_string(self) -> str:
        elements_string: str = functools.reduce(
            lambda v1, v2: v1 + ", " + v2,
            map(lambda v: v[0].to_string() + ": " + v[1].to_string(), self.values)
        )
        return f"[{elements_string}]"


class SchemaValue(PetlValue):
    def __init__(self, petl_type: PetlType, values: List[Tuple[StringValue, PetlType]]):
        PetlValue.__init__(self, petl_type)
        self.values = values

    def to_string(self) -> str:
        elements_string: str = functools.reduce(
            lambda v1, v2: v1 + ", " + v2,
            map(lambda v: v[0].to_string() + ": " + v[1].to_string(), self.values)
        )
        return "${" + elements_string + "}"


class TableValue(PetlValue):
    def __init__(self, petl_type: PetlType, schema: SchemaValue, rows: List[PetlValue]):
        PetlValue.__init__(self, petl_type)
        self.schema = schema
        self.rows = rows

    def to_string(self) -> str:
        return "not-supported"


class FuncValue(PetlValue):
    def __init__(self, petl_type: PetlType, builtin, parameters: List[Tuple[str, PetlType]], body: Expression):
        PetlValue.__init__(self, petl_type)
        self.builtin = builtin
        self.parameters = parameters
        self.body = body

    def to_string(self) -> str:
        return "not-supported"
