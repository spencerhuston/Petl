from typing import Dict

from src.semantic_defintions.petl_types import PetlType, NoneType
from src.semantic_defintions.petl_value import PetlValue, NoneValue
from src.tokens.petl_token import Token


class InterpreterEnvironment:
    map: Dict[str, PetlValue] = {}
    aliases: Dict[str, PetlType] = {}

    def __init__(self):
        self.map = {}
        self.aliases = {}

    def add(self, identifier: str, value: PetlValue):
        self.map[identifier] = value

    def add_alias(self, identifier: str, alias_type: PetlType):
        self.aliases[identifier] = alias_type

    def get(self, identifier: str, token: Token, error) -> PetlValue:
        if identifier in self.map:
            return self.map[identifier]
        else:
            error(f"Identifier \'{identifier}\' does not exist in this scope", token)
            return NoneValue()

    def get_alias(self, alias: str, token: Token, error) -> PetlType:
        if alias in self.aliases:
            return self.aliases[alias]
        else:
            error(f"Alias \'{alias}\' does not exist in this scope", token)
            return NoneType()

    # def get_mappings(self) -> Tuple[Dict[str, PetlValue], Dict[str, PetlType]]:
    #     return dict(self.map), dict(self.aliases)


def copy_environment(environment: InterpreterEnvironment) -> InterpreterEnvironment:
    new_environment: InterpreterEnvironment = InterpreterEnvironment()
    new_environment.map = dict(environment.map)
    new_environment.aliases = dict(environment.aliases)
    return new_environment
