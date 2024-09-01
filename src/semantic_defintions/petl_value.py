from pprint import pformat
from typing import Tuple

from src.semantic_defintions.petl_expression import Expression
from src.semantic_defintions.petl_types import *


class PetlValue(ABC):
    petl_type: PetlType = UnknownType()

    def to_string(self) -> str:
        return pformat(self)


def values_equal(value1: PetlValue, value2: PetlValue) -> bool:
    if isinstance(value1, IntValue) and isinstance(value2, IntValue):
        return value1.value == value2.value
    elif isinstance(value1, BoolValue) and isinstance(value2, BoolValue):
        return value1.value == value2.value
    elif isinstance(value1, CharValue) and isinstance(value2, CharValue):
        return value1.value == value2.value
    elif isinstance(value1, StringValue) and isinstance(value2, StringValue):
        return value1.value == value2.value
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
        self.petl_type: PetlType = IntType()
        self.value: int = value


class BoolValue(PetlValue):
    def __init__(self, value: bool):
        self.petl_type: PetlType = BoolType()
        self.value: bool = value


class CharValue(PetlValue):
    def __init__(self, value: str):
        self.petl_type: PetlType = CharType()
        self.value: str = value


class StringValue(PetlValue):
    def __init__(self, value: str):
        self.petl_type: PetlType = StringType()
        self.value: str = value


class NoneValue(PetlValue):
    def __init__(self):
        self.petl_type: PetlType = NoneType()
        self.value: None = None


class ListValue(PetlValue):
    def __init__(self, petl_type: PetlType, values: List[PetlValue]):
        self.petl_type = petl_type
        self.values = values


class TupleValue(PetlValue):
    def __init__(self, petl_type: PetlType, values: List[PetlValue]):
        self.petl_type = petl_type
        self.values = values


class DictValue(PetlValue):
    def __init__(self, petl_type: PetlType, values: List[Tuple[PetlValue, PetlValue]]):
        self.petl_type = petl_type
        self.values = values


class SchemaValue(PetlValue):
    def __init__(self, petl_type: PetlType, values: List[Tuple[StringValue, PetlType]]):
        self.petl_type = petl_type
        self.values = values


class TableValue(PetlValue):
    def __init__(self, petl_type: PetlType, schema: SchemaValue, rows: List[PetlValue]):
        self.petl_type = petl_type
        self.schema = schema
        self.rows = rows


class LambdaValue(PetlValue):
    def __init__(self, builtin: bool, parameters: List[Tuple[str, PetlType]], body: Expression, environment):
        self.builtin = builtin
        self.parameters = parameters
        self.body = body
        self.environment = environment
