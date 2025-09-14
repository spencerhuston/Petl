from typing import List, Tuple

from src.semantic_defintions.petl_value import PetlValue, IntValue, BoolValue, CharValue, StringValue
from src.utils.query.query_environment import QueryEnvironment
from src.utils.query.query_expression import QueryExpression
from src.utils.query.query_interpreter import QueryInterpreter
from src.utils.query.query_lexer import QueryLexer
from src.utils.query.query_parser import QueryParser
from src.utils.query.query_token import QueryToken
from src.utils.query.query_value import QueryValue, QueryIntValue, QueryBoolValue, QueryCharValue, QueryStringValue


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
    try:
        tokens: List[QueryToken] = QueryLexer().scan(query_text)
        query_ast_root: QueryExpression = QueryParser().parse(tokens)
        environment = QueryEnvironment()
        for variable in variables:
            environment.add(identifier=variable[0], value=petl_to_query_value(variable[1]))
        query_result_value: QueryValue = QueryInterpreter().interpret(query_ast_root, environment)
        if isinstance(query_result_value, QueryBoolValue):
            return query_result_value.value
    except Exception as query_exception:
        error(f"Query failed: {query_exception}", token)
    return False
