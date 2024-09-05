from src.builtins.petl_builtin_definitions import Builtin
from src.phases.environment import InterpreterEnvironment
from src.semantic_defintions.petl_expression import Application
from src.semantic_defintions.petl_value import *
from src.tokens.petl_keyword import Keyword


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


class ToStr(Builtin):
    def __init__(self):
        parameters = [("v", AnyType())]
        Builtin.__init__(self, Keyword.TOSTR.value, parameters, StringType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        return StringValue(environment.get("v", application.token, error).to_string())


class ToUpper:
    pass


class ToLower:
    pass


class StartsWith:
    pass


class EndsWith:
    pass
