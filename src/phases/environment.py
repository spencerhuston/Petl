from typing import Dict

from src.semantic_defintions.petl_types import PetlType, NoneType
from src.semantic_defintions.petl_value import PetlValue, NoneValue
from src.tokens.petl_token import Token
from src.utils.log import Log


class InterpreterEnvironment:
    _map: Dict[str, PetlValue] = {}
    _aliases: Dict[str, PetlType] = {}

    def add(self, identifier: str, value: PetlValue):
        self._map[identifier] = value

    def add_alias(self, identifier: str, alias_type: PetlType):
        self._aliases[identifier] = alias_type

    def get(self, identifier: str, token: Token, logger: Log) -> PetlValue:
        if identifier in self._map:
            return self._map[identifier]
        else:
            logger.error(f"Identifier {identifier} does not exist in this scope\n{token.file_position.to_string()}")
            return NoneValue()

    def get_alias(self, alias: str, token: Token, logger: Log) -> PetlType:
        if alias in self._aliases:
            return self._aliases[alias]
        else:
            logger.error(f"Alias {alias} does not exist in this scope\n{token.file_position.to_string()}")
            return NoneType()