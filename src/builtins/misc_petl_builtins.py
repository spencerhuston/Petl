import random

from src.builtins.petl_builtin_definitions import Builtin
from src.phases.environment import InterpreterEnvironment
from src.semantic_defintions.petl_expression import Application
from src.semantic_defintions.petl_value import *
from src.tokens.petl_keyword import Keyword


class Type(Builtin):
    def __init__(self):
        parameters = [("value", AnyType())]
        Builtin.__init__(self, Keyword.TYPE.value, parameters, StringType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        return StringValue(environment.get("value", application.token, error).petl_type.to_string())


class Rand(Builtin):
    def __init__(self):
        parameters = [
            ("lower", IntType()),
            ("upper", IntType()),
        ]
        Builtin.__init__(self, Keyword.RAND.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        lower_value: PetlValue = environment.get("lower", application.token, error)
        upper_value: PetlValue = environment.get("upper", application.token, error)
        if isinstance(lower_value, IntValue) and isinstance(upper_value, IntValue):
            return IntValue(random.randint(lower_value.value, upper_value.value))
        return NoneValue()
