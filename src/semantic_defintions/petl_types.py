import functools
from abc import ABC, abstractmethod
from typing import List


class PetlType(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass


def _type_list_to_string(main_type: str, type_list: List[PetlType]) -> str:
    type_list_str = functools.reduce(
        lambda a, b: a + ", " + b,
        [petl_type.to_string() for petl_type in type_list]
    )
    return f"{main_type}[{type_list_str}]"


class AnyType(PetlType):
    def to_string(self) -> str:
        return "any"


class UnknownType(PetlType):
    def to_string(self) -> str:
        return "unknown"


class IntType(PetlType):
    def to_string(self) -> str:
        return "int"


class BoolType(PetlType):
    def to_string(self) -> str:
        return "bool"


class CharType(PetlType):
    def to_string(self) -> str:
        return "char"


class StringType(PetlType):
    def to_string(self) -> str:
        return "string"


class NoneType(PetlType):
    def to_string(self) -> str:
        return "none"


class UnionType(PetlType):
    union_types: List[PetlType] = []

    def to_string(self) -> str:
        return _type_list_to_string("union", self.union_types)


class ListType(PetlType):
    list_type: PetlType = UnknownType()

    def to_string(self) -> str:
        return f"list[{self.list_type}]"


class TupleType(PetlType):
    tuple_types: List[PetlType] = []

    def to_string(self) -> str:
        return _type_list_to_string("tuple", self.tuple_types)


class DictType(PetlType):
    key_type: PetlType = UnknownType()
    value_type: PetlType = UnknownType()

    def to_string(self) -> str:
        return f"dict[{self.key_type}:{self.value_type}]"


class SchemaType(PetlType):
    column_types: List[PetlType] = []

    def to_string(self) -> str:
        return _type_list_to_string("schema", self.column_types)


class TableType(PetlType):
    schema_type: SchemaType = SchemaType()

    def to_string(self) -> str:
        return f"table[{self.schema_type.to_string()}]"


class FunctionType(PetlType):
    parameter_types: List[PetlType] = []
    return_type: PetlType = UnknownType()

    def to_string(self) -> str:
        parameter_type_list_str = functools.reduce(
            lambda a, b: a + ", " + b,
            [petl_type.to_string() for petl_type in self.parameter_types]
        )
        return f"({parameter_type_list_str}) -> {self.return_type}"
