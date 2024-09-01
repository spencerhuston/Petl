from typing import Tuple

from src.phases.environment import InterpreterEnvironment
from src.semantic_defintions.petl_expression import Expression, UnknownExpression
from src.semantic_defintions.petl_types import *
from src.semantic_defintions.petl_value import PetlValue, NoneValue, LambdaValue, StringValue
from src.utils.log import Log


class Builtin(ABC):
    name: str
    lambda_type: LambdaType

    @abstractmethod
    def evaluate(self, argument_values: List[PetlValue], environment: InterpreterEnvironment, logger: Log) -> PetlValue:
        pass

    @abstractmethod
    def to_value(self) -> LambdaValue:
        pass

    def _to_value(self, parameters: List[Tuple[str, PetlType]]) -> LambdaValue:
        body: Expression = UnknownExpression()
        environment: InterpreterEnvironment = InterpreterEnvironment()
        return LambdaValue(self.lambda_type, self, parameters, body, environment)


def get_builtin(name: str) -> Builtin:
    if name == "readln":
        return ReadLn()
    elif name == "print":
        return Print()
    elif name == "println":
        return PrintLn()


class ReadLn(Builtin):
    def __init__(self):
        self.name = "readln"
        self.lambda_type = LambdaType([], StringType())

    def evaluate(self, argument_values: List[PetlValue], environment: InterpreterEnvironment, logger: Log) -> PetlValue:
        return StringValue(input())

    def to_value(self) -> LambdaValue:
        parameters = []
        return self._to_value(parameters)


class Print(Builtin):
    def __init__(self):
        self.name = "print"
        self.lambda_type = LambdaType([AnyType()], NoneType())

    def evaluate(self, argument_values: List[PetlValue], environment: InterpreterEnvironment, logger: Log) -> PetlValue:
        print(argument_values[0].to_string().encode().decode('unicode_escape'), end="")
        return NoneValue()

    def to_value(self) -> LambdaValue:
        parameters = [("str", AnyType())]
        return self._to_value(parameters)


class PrintLn(Builtin):
    def __init__(self):
        self.name = "println"
        self.lambda_type = LambdaType([AnyType()], NoneType())

    def evaluate(self, argument_values: List[PetlValue], environment: InterpreterEnvironment, logger: Log) -> PetlValue:
        print(argument_values[0].to_string().encode().decode('unicode_escape'))
        return NoneValue()

    def to_value(self) -> LambdaValue:
        parameters = [("str", AnyType())]
        return self._to_value(parameters)
