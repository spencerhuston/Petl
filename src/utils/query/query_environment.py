from typing import Dict

from src.utils.query.query_value import QueryValue


class QueryEnvironment:
    map: Dict[str, QueryValue] = {}

    def __init__(self):
        self.map = {}

    def add(self, identifier: str, value: QueryValue):
        self.map[identifier] = value

    def get(self, identifier: str) -> QueryValue:
        if identifier in self.map:
            return self.map[identifier]
        else:
            raise Exception(f"Identifier \'{identifier}\' does not exist in this scope")
