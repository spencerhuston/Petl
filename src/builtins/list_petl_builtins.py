from src.builtins.petl_builtin_definitions import Builtin, extract_element_type
from src.phases.environment import InterpreterEnvironment
from src.semantic_defintions.petl_expression import Application
from src.semantic_defintions.petl_value import *
from src.tokens.petl_keyword import Keyword


class Insert:
    pass


class Remove:
    pass


class Replace:
    pass


class Front:
    pass


class Back:
    pass


class Head:
    pass


class Tail:
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


class Contains:
    pass


class Find:
    pass


class Fill:
    pass


class Reverse:
    pass


class Set:
    pass


class Intersect:
    pass
