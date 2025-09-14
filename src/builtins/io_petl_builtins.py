from src.builtins.petl_builtin_definitions import Builtin
from src.phases.interpreter.definitions.value import *
from src.phases.interpreter.environment import InterpreterEnvironment
from src.phases.lexer.definitions.keyword import Keyword
from src.phases.parser.defintions.expression import Application


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