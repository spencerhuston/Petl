from src.builtins.petl_builtin_definitions import Builtin
from src.phases.environment import InterpreterEnvironment
from src.semantic_defintions.petl_expression import Application
from src.semantic_defintions.petl_value import *
from src.tokens.petl_keyword import Keyword


class ToInt(Builtin):
    def __init__(self):
        parameters = [("s", StringType())]
        Builtin.__init__(self, Keyword.TOINT.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        value: PetlValue = environment.get("s", application.token, error)
        if isinstance(value, StringValue):
            return IntValue(int(value.value))
        return NoneValue()


class Sum:
    pass


class Product:
    pass


class Max:
    pass


class Min:
    pass


class Sort:
    pass
