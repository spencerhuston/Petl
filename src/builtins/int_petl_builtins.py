from src.builtins.petl_builtin_definitions import Builtin
from src.phases.interpreter.definitions.value import *
from src.phases.interpreter.environment import InterpreterEnvironment
from src.phases.lexer.definitions.keyword import Keyword
from src.phases.parser.defintions.expression import Application


class ToInt(Builtin):
    def __init__(self):
        parameters = [("s", StringType())]
        Builtin.__init__(self, Keyword.TOINT.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        value: PetlValue = environment.get("s", application.token, error)
        if isinstance(value, StringValue):
            return IntValue(int(value.value))
        return NoneValue()


class Sum(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(IntType()))
        ]
        Builtin.__init__(self, Keyword.SUM.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        if isinstance(list_value, ListValue):
            int_values: List[PetlValue] = list_value.values
            if int_values:
                sum_value: int = 0
                for value in int_values:
                    if isinstance(value, IntValue):
                        sum_value += value.value
                return IntValue(sum_value)
        return NoneValue()


class Product(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(IntType()))
        ]
        Builtin.__init__(self, Keyword.PRODUCT.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        if isinstance(list_value, ListValue):
            int_values: List[PetlValue] = list_value.values
            if int_values:
                product_value: int = 1
                for value in int_values:
                    if isinstance(value, IntValue):
                        product_value *= value.value
                return IntValue(product_value)
        return NoneValue()


class Max(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(IntType()))
        ]
        Builtin.__init__(self, Keyword.MAX.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        if isinstance(list_value, ListValue):
            int_values: List[PetlValue] = list_value.values
            if int_values and isinstance(int_values[0], IntValue):
                max_value: IntValue = int_values[0]
                for value in int_values[1:]:
                    if isinstance(value, IntValue):
                        max_value = value if value.value > max_value.value else max_value
                return max_value
        return NoneValue()


class Min(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(IntType()))
        ]
        Builtin.__init__(self, Keyword.MIN.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        if isinstance(list_value, ListValue):
            int_values: List[PetlValue] = list_value.values
            if int_values and isinstance(int_values[0], IntValue):
                min_value: IntValue = int_values[0]
                for value in int_values[1:]:
                    if isinstance(value, IntValue):
                        min_value = value if value.value < min_value.value else min_value
                return min_value
        return NoneValue()


class Sort(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(IntType()))
        ]
        Builtin.__init__(self, Keyword.SORT.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        if isinstance(list_value, ListValue):
            int_values: List[PetlValue] = list_value.values
            if int_values:
                sorted_values: List[PetlValue] = sorted(int_values, key=lambda v: v.value)
                return ListValue(ListType(IntType()), sorted_values)
            return list_value
        return NoneValue()
