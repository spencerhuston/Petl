from copy import deepcopy

from src.builtins.builtin_definitions import extract_iterable_values, Builtin
from src.phases.interpreter.definitions.value import *
from src.phases.interpreter.environment import copy_environment, InterpreterEnvironment
from src.phases.interpreter.type_resolution import types_conform
from src.phases.lexer.definitions.keyword_petl import Keyword
from src.phases.lexer.definitions.token_petl import Token
from src.phases.parser.defintions.expression import Application


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
            element_type: PetlType = UnknownType()
            element_values: List[PetlValue] = []
            if name == "map":
                element_type = function_value.petl_type.return_type
                element_values = list(map(lambda v: evaluate_element([v], function_value, element_type, function_value.environment, interpreter), iterable_values))
            elif name == "filter":
                element_type = function_value.petl_type.parameter_types[0]

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
