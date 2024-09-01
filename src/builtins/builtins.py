from abc import ABC, abstractmethod
from typing import List

from src.phases.environment import InterpreterEnvironment
from src.phases.petl_phase import PetlPhase
from src.semantic_defintions.petl_types import PetlType, LambdaType
from src.semantic_defintions.petl_value import PetlValue, NoneValue


class Builtin(ABC, PetlPhase):
    def __init__(self, debug=False):
        self.logger.__init__(debug)
        self.petl_type: LambdaType = LambdaType()
        self.parameters: List[str, PetlType] = []
        self.return_type: PetlType
        self.environment: InterpreterEnvironment = InterpreterEnvironment()

    @abstractmethod
    def evaluate(self, arguments: List[PetlValue], environment: InterpreterEnvironment) -> PetlValue:
        pass


def get_builtin(name: str) -> Builtin:
    if name == "readln":
        return ReadLn()
    elif name == "print":
        return Print()
    elif name == "println":
        return PrintLn()


class ReadLn(Builtin):
    pass


class Print(Builtin):
    pass


class PrintLn(Builtin):
    def evaluate(self, arguments: List[PetlValue], environment: InterpreterEnvironment) -> PetlValue:
        if len(arguments) != 1:
            self.logger.error(f"println requires 1 argument")
            return NoneValue()
