from typing import List, Tuple

from src.phases.interpreter.definitions.value import PetlValue, IntValue, BoolValue, CharValue, StringValue
from src.query.interpreter.environment import QueryEnvironment
from src.query.interpreter.interpreter import QueryInterpreter
from src.query.interpreter.value import QueryValue, QueryIntValue, QueryBoolValue, QueryCharValue, QueryStringValue
from src.query.lexer.lexer import QueryLexer
from src.query.lexer.query_token import QueryToken
from src.query.parser.expression import QueryExpression
from src.query.parser.parser import QueryParser


def petl_to_query_value(value: PetlValue) -> QueryValue:
    if isinstance(value, IntValue):
        return QueryIntValue(value.value)
    elif isinstance(value, BoolValue):
        return QueryBoolValue(value.value)
    elif isinstance(value, CharValue):
        return QueryCharValue(value.value)
    elif isinstance(value, StringValue):
        return QueryStringValue(value.value)
    else:
        raise Exception(f"Invalid type for query: {value.petl_type.to_string()}")


def execute_query(query_text: str, variables: List[Tuple[str, PetlValue]], token, error) -> bool:
    tokens: List[QueryToken] = QueryLexer().scan(query_text)
    query_ast_root: QueryExpression = QueryParser().parse(tokens)
    environment = QueryEnvironment()
    for variable in variables:
        environment.add(identifier=variable[0], value=petl_to_query_value(variable[1]))
    query_result_value: QueryValue = QueryInterpreter().interpret(query_ast_root, environment, token, error)
    if isinstance(query_result_value, QueryBoolValue):
        return query_result_value.value
