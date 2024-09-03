from typing import Any, Optional

from src.phases.environment import InterpreterEnvironment, copy_environment
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
        return FuncValue(self.func_type, self, self.parameters, UnknownExpression())


def extract_iterable_values(name: str, iterable_value: PetlValue, token: Token, error) -> Optional[List[Any]]:
    if isinstance(iterable_value, ListValue) and isinstance(iterable_value.petl_type, ListType):
        return iterable_value.values
    elif isinstance(iterable_value, TupleValue) and isinstance(iterable_value.petl_type, TupleType):
        return iterable_value.values
    elif isinstance(iterable_value, DictValue) and isinstance(iterable_value.petl_type, DictType):
        return iterable_value.values
    elif isinstance(iterable_value, TableValue) and isinstance(iterable_value.petl_type, TableType):
        return iterable_value.rows
    else:
        error(f"{name} function requires iterable type, not {iterable_value.petl_type.to_string()}", token)
        return None


def extract_element_type(iterable_value: PetlValue) -> PetlType:
    if isinstance(iterable_value.petl_type, ListType):
        return iterable_value.petl_type.list_type
    elif isinstance(iterable_value.petl_type, TupleType):
        return UnionType(iterable_value.petl_type.tuple_types)
    elif isinstance(iterable_value.petl_type, DictType):
        return iterable_value.petl_type
    elif isinstance(iterable_value.petl_type, TableType):
        return UnionType(iterable_value.petl_type.schema_type.column_types)
    else:
        NoneType()


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
        print(value.to_string().replace('\'', '').replace('\"', '').encode().decode('unicode_escape'), end="")
        return NoneValue()


class PrintLn(Builtin):
    def __init__(self):
        Builtin.__init__(self, Keyword.PRINTLN.value, [("value", AnyType())], NoneType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        value: PetlValue = environment.get("value", application.token, error)
        print(value.to_string().replace('\'', '').replace('\"', '').encode().decode('unicode_escape'))
        return NoneValue()


class Map(Builtin):
    def __init__(self):
        parameters = [
            ("iterable", IterableType()),
            ("mapping_function", FuncType([AnyType()], AnyType()))
        ]
        Builtin.__init__(self, Keyword.MAP.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        iterable_value: PetlValue = environment.get("iterable", application.token, error)
        mapping_value: PetlValue = environment.get("mapping_function", application.token, error)
        if isinstance(mapping_value.petl_type, FuncType) and isinstance(mapping_value, FuncValue):
            element_type: PetlType = mapping_value.petl_type.return_type
            mapping_function_value: FuncValue = mapping_value
            iterable_values = extract_iterable_values(self.name, iterable_value, application.token, error)
            if iterable_values:
                def evaluate_element(value: PetlValue, function_value: FuncValue) -> PetlValue:
                    body_environment: InterpreterEnvironment = copy_environment(environment)
                    argument_identifier: str = function_value.parameters[0][0]
                    body_environment.add(argument_identifier, value)
                    return interpreter.evaluate(function_value.body, body_environment, element_type)

                element_values: List[PetlValue] = list(map(lambda v: evaluate_element(v, mapping_function_value), iterable_values))
                return ListValue(element_type, element_values)
        return NoneValue()


class Filter(Builtin):
    def __init__(self):
        parameters = [
            ("iterable", IterableType()),
            ("mapping_function", FuncType([AnyType()], BoolType()))
        ]
        Builtin.__init__(self, Keyword.FILTER.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        iterable_value: PetlValue = environment.get("iterable", application.token, error)
        filter_value: PetlValue = environment.get("filter_function", application.token, error)
        if isinstance(filter_value.petl_type, FuncType) and isinstance(filter_value, FuncValue):
            element_type: PetlType = filter_value.petl_type.return_type
            mapping_function_value: FuncValue = filter_value
            iterable_values = extract_iterable_values(self.name, iterable_value, application.token, error)
            if iterable_values:
                def evaluate_element(value: PetlValue, function_value: FuncValue) -> bool:
                    body_environment: InterpreterEnvironment = copy_environment(environment)
                    argument_identifier: str = function_value.parameters[0][0]
                    body_environment.add(argument_identifier, value)
                    result: PetlValue = interpreter.evaluate(function_value.body, body_environment, element_type)
                    if isinstance(result, BoolValue):
                        return result.value
                    else:
                        return False

                element_values: List[PetlValue] = list(filter(lambda v: evaluate_element(v, mapping_function_value), iterable_values))
                return ListValue(element_type, element_values)
        return NoneValue()


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


class Foldl(Builtin):
    pass


class Foldr(Builtin):
    pass


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
        if isinstance(iterable_value, ListValue):
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
            ("path", StringType()),
            ("headers", BoolType())
        ]
        Builtin.__init__(self, Keyword.CREATETABLE.value, parameters, TableType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        pass


class ReadCsv(Builtin):
    pass


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
