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
        start_value: PetlValue = environment.get("start", application.token, error)
        end_value: PetlValue = environment.get("end", application.token, error)

        if isinstance(string_value, StringValue) and isinstance(start_value, IntValue) and isinstance(end_value, IntValue):
            string: str = string_value.value
            start: int = start_value.value
            end: int = end_value.value

            if start < 0 or end < 0 or \
                    start >= len(string) or end >= len(string) or \
                    start > end:
                error(f"Invalid substr range value(s)", application.token)
                return NoneValue()

            return StringValue(string[start:end])
        return NoneValue()


class ToStr(Builtin):
    def __init__(self):
        parameters = [("v", AnyType())]
        Builtin.__init__(self, Keyword.TOSTR.value, parameters, StringType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        return StringValue(environment.get("v", application.token, error).to_string())


class ToUpper(Builtin):
    def __init__(self):
        parameters = [("s", StringType())]
        Builtin.__init__(self, Keyword.TOUPPER.value, parameters, StringType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        s_value: PetlValue = environment.get("s", application.token, error)
        if isinstance(s_value, StringValue):
            string: str = s_value.value
            return StringValue(string.upper())
        return NoneValue()


class ToLower(Builtin):
    def __init__(self):
        parameters = [("s", StringType())]
        Builtin.__init__(self, Keyword.TOLOWER.value, parameters, StringType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        s_value: PetlValue = environment.get("s", application.token, error)
        if isinstance(s_value, StringValue):
            string: str = s_value.value
            return StringValue(string.lower())
        return NoneValue()


class StartsWith(Builtin):
    def __init__(self):
        parameters = [
            ("s1", StringType()),
            ("s2", StringType()),
        ]
        Builtin.__init__(self, Keyword.STARTSWITH.value, parameters, BoolType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        s1_value: PetlValue = environment.get("s1", application.token, error)
        s2_value: PetlValue = environment.get("s2", application.token, error)
        if isinstance(s1_value, StringValue) and isinstance(s2_value, StringValue):
            return BoolValue(s1_value.value.startswith(s2_value.value))
        return BoolValue(False)


class EndsWith(Builtin):
    def __init__(self):
        parameters = [
            ("s1", StringType()),
            ("s2", StringType()),
        ]
        Builtin.__init__(self, Keyword.ENDSWITH.value, parameters, BoolType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        s1_value: PetlValue = environment.get("s1", application.token, error)
        s2_value: PetlValue = environment.get("s2", application.token, error)
        if isinstance(s1_value, StringValue) and isinstance(s2_value, StringValue):
            return BoolValue(s1_value.value.endswith(s2_value.value))
        return BoolValue(False)
