from typing import Optional

from src.utils.query.query_types import QueryType, QueryUnknownType


def _types_conform(expression_type: QueryType, expected_type: QueryType) -> QueryType:
    if not isinstance(expression_type, QueryUnknownType) and isinstance(expected_type, QueryUnknownType):
        return expression_type
    elif isinstance(expression_type, QueryUnknownType) and not isinstance(expected_type, QueryUnknownType):
        return expected_type
    elif not isinstance(expression_type, QueryUnknownType) and not isinstance(expected_type, QueryUnknownType):
        if type(expression_type) is type(expected_type):
            return expression_type
        else:
            return QueryUnknownType()
    else:
        return QueryUnknownType()


def types_conform(expression_type: QueryType, expected_type: QueryType) -> Optional[QueryType]:
    conformed_type: QueryType = _types_conform(expression_type, expected_type)
    if isinstance(conformed_type, QueryUnknownType):
        raise Exception(f"Type mismatch: {expression_type.to_string()} vs. {expected_type.to_string()}")
    else:
        return conformed_type
