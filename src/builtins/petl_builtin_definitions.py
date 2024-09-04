import csv
from copy import deepcopy
from typing import Any, Optional

from src.phases.environment import InterpreterEnvironment, copy_environment
from src.phases.type_resolver import types_conform
from src.semantic_defintions.petl_expression import UnknownExpression, Application
from src.semantic_defintions.petl_value import *
from src.tokens.petl_keyword import Keyword
from src.tokens.petl_token import Token


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


def from_string_value(value: StringValue) -> PetlValue:
    if not value:
        return NoneValue()
    elif value.value.isnumeric():
        return IntValue(int(value.value))
    elif value.value == "true" or value.value == "false":
        return BoolValue(True if value.value == "true" else False)
    else:
        return value


def fold_types_conform(init: PetlType, p1: PetlType, p2: PetlType, rt: PetlType, token: Token, error) -> bool:
    def text_types_conform() -> bool:
        return isinstance(init, CharType) and \
               isinstance(p1, CharType) and \
               isinstance(p2, CharType) and \
               isinstance(rt, StringType)

    return text_types_conform() or \
           (types_conform(token, init, p1, error) is not None and
            types_conform(token, p1, p2, error) is not None and
            types_conform(token, p2, rt, error) is not None)


class ReadLn(Builtin):
    def __init__(self):
        Builtin.__init__(self, Keyword.READLN.value, [], StringType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        return StringValue(input())


class Print(Builtin):
    def __init__(self):
        Builtin.__init__(self, Keyword.PRINT.value, [("value", AnyType())], NoneType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        value: PetlValue = environment.get("value", application.token, error)
        print(value.to_string().encode().decode('unicode_escape'), end="")
        return NoneValue()


class PrintLn(Builtin):
    def __init__(self):
        Builtin.__init__(self, Keyword.PRINTLN.value, [("value", AnyType())], NoneType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        value: PetlValue = environment.get("value", application.token, error)
        print(value.to_string().encode().decode('unicode_escape'))
        return NoneValue()


def evaluate_element(values: List[PetlValue], function_value: FuncValue, element_type: PetlType, environment, interpreter) -> PetlValue:
    body_environment: InterpreterEnvironment = copy_environment(environment)
    for i, value in enumerate(values):
        argument_identifier: str = function_value.parameters[i][0]
        if isinstance(value, tuple):
            tuple_type: TupleType = TupleType([value[0].petl_type, value[1].petl_type])
            tuple_value: TupleValue = TupleValue(tuple_type, [value[0], value[1]])
            body_environment.add(argument_identifier, tuple_value)
        else:
            body_environment.add(argument_identifier, value)
    return interpreter.evaluate(function_value.body, body_environment, element_type)


def get_text_mapping(iterable_value: PetlValue, element_type: PetlType, element_values: List[PetlValue]) -> PetlValue:
    if isinstance(iterable_value.petl_type, StringType):
        def extract_char_value(c1: CharValue) -> str:
            return c1.value

        element_str_values: List[str] = list(map(lambda c: extract_char_value(c), element_values))
        return StringValue(functools.reduce(lambda c1, c2: c1 + c2, element_str_values))
    else:
        return ListValue(ListType(element_type), element_values)


def evaluate_higher_order_function(name, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
    iterable_value: PetlValue = environment.get("iterable", application.token, error)
    function_value: PetlValue = environment.get("function_value", application.token, error)
    if isinstance(function_value.petl_type, FuncType) and isinstance(function_value, FuncValue):
        function_value: FuncValue = function_value
        iterable_values = extract_iterable_values(name, iterable_value, application.token, error)
        if iterable_values:
            element_values: List[PetlValue] = []
            if name == "map":
                element_type: PetlType = function_value.petl_type.return_type
                element_values = list(map(lambda v: evaluate_element([v], function_value, element_type, function_value.environment, interpreter), iterable_values))
            elif name == "filter":
                element_type: PetlType = function_value.petl_type.parameter_types[0]

                def evaluate_bool_element(value: PetlValue) -> bool:
                    result: PetlValue = evaluate_element([value], function_value, BoolType(), function_value.environment, interpreter)
                    if isinstance(result, BoolValue):
                        return result.value
                    else:
                        return False

                element_values = list(filter(lambda v: evaluate_bool_element(v), iterable_values))
            return get_text_mapping(iterable_value, element_type, element_values)
    return NoneValue()


class Map(Builtin):
    def __init__(self):
        parameters = [
            ("iterable", IterableType()),
            ("function_value", FuncType([AnyType()], AnyType()))
        ]
        Builtin.__init__(self, Keyword.MAP.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        return evaluate_higher_order_function("map", application, environment, interpreter, error)


class Filter(Builtin):
    def __init__(self):
        parameters = [
            ("iterable", IterableType()),
            ("function_value", FuncType([AnyType()], BoolType()))
        ]
        Builtin.__init__(self, Keyword.FILTER.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        return evaluate_higher_order_function("filter", application, environment, interpreter, error)


class Zip(Builtin):
    def __init__(self):
        parameters = [
            ("iterable1", IterableType()),
            ("iterable2", IterableType()),
        ]
        Builtin.__init__(self, Keyword.ZIP.value, parameters, ListType(TupleType([AnyType(), AnyType()])))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        iterable1_value: PetlValue = environment.get("iterable1", application.token, error)
        iterable2_value: PetlValue = environment.get("iterable2", application.token, error)
        iterable1_values = extract_iterable_values(self.name, iterable1_value, application.token, error)
        iterable2_values = extract_iterable_values(self.name, iterable2_value, application.token, error)
        if iterable1_values and iterable2_values:
            if len(iterable1_values) == len(iterable2_values):
                iterable1_element_type: PetlType = extract_element_type(iterable1_value)
                iterable2_element_type: PetlType = extract_element_type(iterable2_value)
                zipped_element_type: TupleType = TupleType([iterable1_element_type, iterable2_element_type])
                zipped_values: List[TupleValue] = list(map(lambda v1, v2: TupleValue(zipped_element_type, [v1, v2]), iterable1_values, iterable2_values))
                return ListValue(ListType(zipped_element_type), zipped_values)
            else:
                error(f"Zip requires iterables of equal length", application.token)
        return NoneValue()


def evaluate_fold(application: Application, environment: InterpreterEnvironment, interpreter, error, reverse: bool) -> PetlValue:
    iterable_value: PetlValue = environment.get("iterable", application.token, error)
    initial_value: PetlValue = environment.get("initial_value", application.token, error)
    function_value: PetlValue = environment.get("fold_function", application.token, error)
    if isinstance(function_value.petl_type, FuncType) and isinstance(iterable_value, ListValue):
        function_type: FuncType = function_value.petl_type
        param1_type: PetlType = function_type.parameter_types[0]
        param2_type: PetlType = function_type.parameter_types[1]

        if fold_types_conform(initial_value.petl_type, param1_type, param2_type, function_type.return_type, application.token, error):
            element_type: PetlType = function_type.return_type

            if isinstance(function_value, FuncValue):
                fold_function_value: FuncValue = function_value
                values: List[PetlValue] = deepcopy(iterable_value.values)
                if reverse:
                    values.reverse()
                values.insert(0, initial_value)

                fold_value: PetlValue = functools.reduce(lambda v1, v2: evaluate_element([v1, v2], fold_function_value, element_type, environment, interpreter), values)
                fold_value.petl_type = element_type
                return fold_value
    return NoneValue()


class Foldl(Builtin):
    def __init__(self):
        parameters = [
            ("iterable", ListType(AnyType())),
            ("initial_value", AnyType()),
            ("fold_function", FuncType([AnyType(), AnyType()], AnyType()))
        ]
        Builtin.__init__(self, Keyword.FOLDL.value, parameters, AnyType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        return evaluate_fold(application, environment, interpreter, error, reverse=False)


class Foldr(Builtin):
    def __init__(self):
        parameters = [
            ("iterable", ListType(AnyType())),
            ("initial_value", AnyType()),
            ("fold_function", FuncType([AnyType(), AnyType()], AnyType()))
        ]
        Builtin.__init__(self, Keyword.FOLDR.value, parameters, AnyType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        return evaluate_fold(application, environment, interpreter, error, reverse=True)


class Slice(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType()),
            ("start", IntType()),
            ("end", IntType())
        ]
        Builtin.__init__(self, Keyword.SLICE.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        start_value: PetlValue = environment.get("string_value", application.token, error)
        end_value: PetlValue = environment.get("string_value", application.token, error)
        element_type: PetlType = extract_element_type(list_value)

        if isinstance(list_value, ListValue) and isinstance(start_value, IntValue) and isinstance(end_value, IntValue):
            list_values: List[PetlValue] = list_value.values
            start: int = start_value.value
            end: int = end_value.value

            if start < 0 or end < 0 or \
                    start >= len(list_values) or end >= len(list_values) or \
                    start_value > end_value:
                error(f"Invalid slice range value(s)", application.token)
                return NoneValue()

            return ListValue(element_type, list_values)
        return NoneValue()


class Substr(Builtin):
    def __init__(self):
        parameters = [
            ("string_value", StringType()),
            ("start", IntType()),
            ("end", IntType())
        ]
        Builtin.__init__(self, Keyword.SUBSTR.value, parameters, StringType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        string_value: PetlValue = environment.get("string_value", application.token, error)
        start_value: PetlValue = environment.get("string_value", application.token, error)
        end_value: PetlValue = environment.get("string_value", application.token, error)

        if isinstance(string_value, StringValue) and isinstance(start_value, IntValue) and isinstance(end_value, IntValue):
            string: str = string_value.value
            start: int = start_value.value
            end: int = end_value.value

            if start < 0 or end < 0 or \
                    start >= len(string) or end >= len(string) or \
                    start_value > end_value:
                error(f"Invalid substr range value(s)", application.token)
                return NoneValue()

            return StringValue(string[start_value:end_value])
        return NoneValue()


class Len(Builtin):
    def __init__(self):
        parameters = [("iterable", IterableType())]
        Builtin.__init__(self, Keyword.LEN.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        iterable_value: PetlValue = environment.get("iterable", application.token, error)
        if isinstance(iterable_value, StringValue):
            return IntValue(len(iterable_value.value))
        elif isinstance(iterable_value, ListValue):
            return IntValue(len(iterable_value.values))
        elif isinstance(iterable_value, TupleValue):
            return IntValue(len(iterable_value.values))
        elif isinstance(iterable_value, DictValue):
            return IntValue(len(iterable_value.values))
        elif isinstance(iterable_value, TableValue):
            return IntValue(len(iterable_value.rows))
        else:
            error(f"Length function requires iterable type, not {iterable_value.petl_type.to_string()}", application.token)
            return NoneValue()


class Type(Builtin):
    def __init__(self):
        parameters = [("value", AnyType())]
        Builtin.__init__(self, Keyword.TYPE.value, parameters, StringType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        return StringValue(environment.get("value", application.token, error).petl_type.to_string())


class ToStr(Builtin):
    def __init__(self):
        parameters = [("v", AnyType())]
        Builtin.__init__(self, Keyword.TOSTR.value, parameters, StringType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        return StringValue(environment.get("v", application.token, error).to_string())


class ToInt(Builtin):
    def __init__(self):
        parameters = [("s", StringType())]
        Builtin.__init__(self, Keyword.TOINT.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        value: PetlValue = environment.get("s", application.token, error)
        if isinstance(value, StringValue):
            return IntValue(int(value.value))
        return NoneValue()


class CreateTable(Builtin):
    def __init__(self):
        parameters = [
            ("schema", SchemaType()),
            ("rows", ListType(TupleType()))
        ]
        Builtin.__init__(self, Keyword.CREATETABLE.value, parameters, TableType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        schema_value: PetlValue = environment.get("schema", application.token, error)
        rows_value: PetlValue = environment.get("rows", application.token, error)
        if isinstance(schema_value, SchemaValue) and isinstance(rows_value, ListValue):
            schema_values: List[Tuple[PetlValue, PetlType]] = schema_value.values
            rows: List[PetlValue] = rows_value.values
            for row in rows:
                if isinstance(row, TupleValue):
                    tuple_value: TupleValue = row
                    zipped_tuple_schema_values = list(map(lambda tv, sv: (tv, sv), tuple_value.values, schema_values))
                    for value, column in zipped_tuple_schema_values:
                        if not types_conform(application.token, value.petl_type, column[1], error):
                            return NoneValue()
            if isinstance(schema_value.petl_type, SchemaType):
                return TableValue(TableType(SchemaType(schema_value.petl_type.column_types)), schema_value, rows)
        return NoneValue()


class ReadCsv(Builtin):
    def __init__(self):
        parameters = [
            ("path", StringType()),
            ("header", BoolType()),
            ("schema", SchemaType())
        ]
        Builtin.__init__(self, Keyword.READCSV.value, parameters, TableType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        path_value: PetlValue = environment.get("path", application.token, error)
        header_value: PetlValue = environment.get("header", application.token, error)
        schema_value: PetlValue = environment.get("schema", application.token, error)

        if isinstance(path_value, StringValue) and isinstance(header_value, BoolValue) and isinstance(schema_value, SchemaValue):
            path_value: StringValue = path_value
            header_value: BoolValue = header_value
            schema_value: SchemaValue = schema_value

            def header_matches_schema(header_row: List[str], schema_value: SchemaValue) -> bool:
                return all(map(lambda h, sv: h == sv[0], header_row, schema_value.values))

            # def row_matches_schema(row: List[str], schema_value: SchemaValue) -> bool:
            #     for value in row:
            #         if types_conform()

            with open(path_value.value + ".csv", mode ='r') as csv_file:
                csv_file_rows: List[List[str]] = list(csv.reader(csv_file))
                if isinstance(schema_value.petl_type, SchemaType):
                    rows: ListValue = ListValue(ListType(TupleType(schema_value.petl_type.column_types)), [])
                    if csv_file_rows:
                        if header_value.value:
                            header_row: List[str] = csv_file_rows[0]
                            if not header_matches_schema(header_row, schema_value):
                                error(f"Provided schema does not match CSV header: {header_row}", application.token)
                                return NoneValue()

                        for row in csv_file_rows:
                            pass


                #else return empty table value

        return NoneValue()

class WriteCsv(Builtin):
    pass


class Join(Builtin):
    pass


class With(Builtin):
    pass


class Where(Builtin):
    pass


class Select(Builtin):
    pass


class Drop(Builtin):
    pass


class Column(Builtin):
    pass


class Collect(Builtin):
    pass


class Count(Builtin):
    pass
