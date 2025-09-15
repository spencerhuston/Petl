from typing import Any, Optional

from src.phases.interpreter.definitions.value import *
from src.phases.interpreter.environment import InterpreterEnvironment
from src.phases.lexer.definitions.token_petl import Token
from src.phases.parser.defintions.expression import UnknownExpression, Application


class Builtin(ABC):
    def __init__(self, name: str, parameters: List[Tuple[str, PetlType]], return_type: PetlType):
        self.name: str = name
        self.parameters: List[Tuple[str, PetlType]] = parameters
        self.func_type = FuncType([parameter[1] for parameter in parameters], return_type)

    @abstractmethod
    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        pass

    def to_value(self) -> FuncValue:
        return FuncValue(self.func_type, self, self.parameters, UnknownExpression(), InterpreterEnvironment())


def extract_iterable_values(name: str, iterable_value: PetlValue, token: Token, error) -> Optional[List[Any]]:
    if isinstance(iterable_value, StringValue) and isinstance(iterable_value.petl_type, StringType):
        return [CharValue(char_value) for char_value in iterable_value.value]
    elif isinstance(iterable_value, ListValue) and isinstance(iterable_value.petl_type, ListType):
        return iterable_value.values
    elif isinstance(iterable_value, TupleValue) and isinstance(iterable_value.petl_type, TupleType):
        return iterable_value.values
    elif isinstance(iterable_value, DictValue) and isinstance(iterable_value.petl_type, DictType):
        return iterable_value.values
    elif isinstance(iterable_value, TableValue) and isinstance(iterable_value.petl_type, TableType):
        return iterable_value.rows
    else:
        error(f"\'{name}\' requires iterable type, not {iterable_value.petl_type.to_string()}", token)
        return None


def extract_element_type(iterable_value: PetlValue) -> PetlType:
    if isinstance(iterable_value.petl_type, StringType):
        return CharType()
    elif isinstance(iterable_value.petl_type, ListType):
        return iterable_value.petl_type.list_type
    elif isinstance(iterable_value.petl_type, TupleType):
        return UnionType(iterable_value.petl_type.tuple_types)
    elif isinstance(iterable_value.petl_type, DictType):
        return TupleType([iterable_value.petl_type.key_type, iterable_value.petl_type.key_type])
    elif isinstance(iterable_value.petl_type, TableType):
        return UnionType(iterable_value.petl_type.schema_type.column_types)
    else:
        NoneType()


def from_string_value(value: str) -> PetlValue:
    if not value:
        return NoneValue()
    elif value.isnumeric():
        return IntValue(int(value))
    elif value == "true" or value == "false":
        return BoolValue(True if value == "true" else False)
    else:
        return StringValue(value)
