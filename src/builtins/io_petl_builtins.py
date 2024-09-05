from src.builtins.petl_builtin_definitions import Builtin
from src.phases.environment import InterpreterEnvironment
from src.semantic_defintions.petl_expression import Application
from src.semantic_defintions.petl_value import *
from src.tokens.petl_keyword import Keyword


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