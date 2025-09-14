from pprint import pformat
from typing import Tuple

from src.phases.interpreter.definitions.types import *
from src.phases.parser.defintions.expression import Expression


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
        return self.value


class StringValue(PetlValue):
    def __init__(self, value: str):
        PetlValue.__init__(self, StringType())
        self.value: str = value

    def to_string(self) -> str:
        return self.value


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
        def row_to_strings(row: List[str]) -> List[str]:
            if isinstance(row, TupleValue):
                return list(map(lambda v: v.to_string(), row.values))
            return []

        header_types_strs: List[str] = list(map(lambda sv: sv[1].to_string(), self.schema.values))
        header_names_strs: List[str] = list(map(lambda sv: sv[0].to_string(), self.schema.values))
        row_value_strs: List[List[str]] = list(map(lambda row: row_to_strings(row), self.rows))

        def get_longest_column_str_length(column: int) -> int:
            string_lengths: List[int] = [len(header_types_strs[column]), len(header_names_strs[column])]
            for row in row_value_strs:
                string_lengths.append(len(row[column]))
            return max(string_lengths)

        column_lengths: List[int] = list(map(lambda c: get_longest_column_str_length(c), range(0, len(header_names_strs))))

        def row_to_string(row: List[str]) -> str:
            return "| " + " | ".join(list(map(lambda i: row[i].ljust(column_lengths[i]), range(0, len(row))))) + " |\n"

        header_types_str: str = row_to_string(header_types_strs)
        banner = " " * (len(header_types_str) - 1) + "\n"
        table_value_str: str = f"\033[4m{banner}\033[1m{header_types_str}{row_to_string(header_names_strs)}\033[0m"
        for row in row_value_strs:
            table_value_str += f"\033[4m{row_to_string(row)}\033[0m"
        return table_value_str


class FuncValue(PetlValue):
    def __init__(self, petl_type: PetlType, builtin, parameters: List[Tuple[str, PetlType]], body: Expression, environment):
        PetlValue.__init__(self, petl_type)
        self.builtin = builtin
        self.parameters = parameters
        self.body = body
        self.environment = environment

    def to_string(self) -> str:
        name: str = f"builtin:{self.builtin.name}" if self.builtin else ""
        return_type: str = self.petl_type.return_type.to_string() if isinstance(self.petl_type, FuncType) else "?"
        parameters: str = ", ".join(list(map(lambda p: p[0] + ": " + p[1].to_string(), self.parameters)))
        return f"{name}({parameters}) -> {return_type}"
