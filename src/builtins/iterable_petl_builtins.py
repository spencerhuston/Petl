from src.builtins.builtin_definitions import Builtin, extract_iterable_values, extract_element_type
from src.phases.interpreter.definitions.value import *
from src.phases.interpreter.environment import InterpreterEnvironment
from src.phases.lexer.definitions.keyword_petl import Keyword
from src.phases.parser.defintions.expression import Application


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


class Len(Builtin):
    def __init__(self):
        parameters = [("iterable", IterableType())]
        Builtin.__init__(self, Keyword.LEN.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        iterable_value: PetlValue = environment.get("iterable", application.token, error)
        return IntValue(len(extract_iterable_values(self.name, iterable_value, application.token, error)))


class IsEmpty(Builtin):
    def __init__(self):
        parameters = [("iterable", IterableType())]
        Builtin.__init__(self, Keyword.LEN.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        iterable_value: PetlValue = environment.get("iterable", application.token, error)
        return BoolValue(len(extract_iterable_values(self.name, iterable_value, application.token, error)) == 0)
