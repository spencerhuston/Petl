from typing import List, Tuple

from src.semantic_defintions.petl_value import PetlValue
from src.utils.query.query_expression import QueryExpression
from src.utils.query.query_lexer import QueryLexer
from src.utils.query.query_parser import QueryParser
from src.utils.query.query_token import QueryToken


def execute_query(query_text: str, variables: List[Tuple[str, PetlValue]], token, error) -> bool:
    lexer = QueryLexer()
    try:
        tokens: List[QueryToken] = lexer.scan(query_text)
        parser = QueryParser()
        query_ast_root: QueryExpression = parser.parse(tokens)
    except Exception as query_exception:
        error(f"Query failed: {query_exception}", token)
    return False
