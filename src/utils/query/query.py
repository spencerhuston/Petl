from typing import List, Tuple

from src.semantic_defintions.petl_value import PetlValue
from src.utils.query.query_lexer import QueryLexer


def execute_query(query_text: str, variables: List[Tuple[str, PetlValue]], token, error) -> bool:
    lexer = QueryLexer()
    try:
        lexer.scan(query_text)
    except Exception as query_exception:
        error(f"Query failed: {query_exception}", token)
    return False
