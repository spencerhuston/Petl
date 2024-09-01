from src.semantic_defintions.petl_expression import *
from src.semantic_defintions.petl_types import *
from src.tokens.petl_token import Token
from src.utils.log import Log


def _make_well_formed(t: PetlType, token: Token) -> PetlType:
    if isinstance(t, UnionType):
        return UnionType(list(map(lambda ut: _make_well_formed(ut, token), t.union_types)))
    elif isinstance(t, ListType):
        return ListType(_make_well_formed(t.list_type, token))
    elif isinstance(t, TupleType):
        return TupleType(list(map(lambda tt: _make_well_formed(tt, token), t.tuple_types)))
    elif isinstance(t, DictType):
        return DictType(_make_well_formed(t.key_type, token), _make_well_formed(t.value_type, token))
    elif isinstance(t, SchemaType):
        return SchemaType(list(map(lambda st: _make_well_formed(st, token), t.column_types)))
    elif isinstance(t, TableType):
        return TableType(SchemaType(list(map(lambda st: _make_well_formed(st, token), t.schema_type.column_types))))
    elif isinstance(t, LambdaType):
        return LambdaType(list(map(lambda pt: _make_well_formed(pt, token), t.parameter_types)), _make_well_formed(t.return_type, token))
    elif not isinstance(t, UnknownType):
        return t
    else:
        return UnknownType()


def _is_well_formed(t: PetlType) -> bool:
    if isinstance(t, UnknownType):
        return False
    elif isinstance(t, UnionType):
        return all(map(lambda ut: _is_well_formed(ut), t.union_types))
    elif isinstance(t, ListType):
        return _is_well_formed(t.list_type)
    elif isinstance(t, TupleType):
        return all(map(lambda tt: _is_well_formed(tt), t.tuple_types))
    elif isinstance(t, DictType):
        return _is_well_formed(t.key_type) and _is_well_formed(t.value_type)
    elif isinstance(t, SchemaType):
        return all(map(lambda st: _is_well_formed(st), t.column_types))
    elif isinstance(t, TableType):
        return all(map(lambda tct: _is_well_formed(tct), t.schema_type.column_types))
    elif isinstance(t, LambdaType):
        return all(map(lambda pt: _is_well_formed(pt), t.parameter_types)) and _is_well_formed(t.return_type)
    else:
        return True


def _collection_types_conform(token: Token, expression_type_list: List[PetlType], expected_type_list: List[PetlType]) -> List[PetlType]:
    zipped_types: List[Tuple[PetlType, PetlType]] = list(map(lambda t1, t2: (t1, t2), expression_type_list, expected_type_list))
    return list(map(lambda t: _types_conform(token, t[0], t[1]), zipped_types))


def _types_conform(token: Token, expression_type: PetlType, expected_type: PetlType) -> PetlType:
    if not isinstance(expression_type, UnknownType) and isinstance(expected_type, UnknownType):
        return _make_well_formed(expression_type, token)
    elif isinstance(expression_type, UnknownType) and not isinstance(expected_type, UnknownType):
        return _make_well_formed(expected_type, token)
    elif isinstance(expression_type, AnyType) and not isinstance(expected_type, AnyType):
        return _make_well_formed(expected_type, token)
    elif not isinstance(expression_type, AnyType) and isinstance(expected_type, AnyType):
        return _make_well_formed(expression_type, token)
    elif isinstance(expression_type, UnionType) and isinstance(expected_type, UnionType):
        return UnionType(
            _collection_types_conform(token, expression_type.union_types, expected_type.union_types))
    elif isinstance(expression_type, UnionType) and not isinstance(expected_type, UnionType) and expected_type in expression_type.union_types:
        return _make_well_formed(expected_type, token)
    elif not isinstance(expression_type, UnionType) and isinstance(expected_type, UnionType) and expression_type in expected_type.union_types:
        return _make_well_formed(expression_type, token)
    elif isinstance(expression_type, ListType) and isinstance(expected_type, ListType):
        return ListType(_types_conform(token, expression_type.list_type, expected_type.list_type))
    elif isinstance(expression_type, TupleType) and isinstance(expected_type, TupleType) and expression_type.tuple_types and expected_type.tuple_types:
        return TupleType(
            _collection_types_conform(token, expression_type.tuple_types, expected_type.tuple_types))
    elif isinstance(expression_type, DictType) and isinstance(expected_type, DictType):
        return DictType(
            _types_conform(token, expression_type.key_type, expected_type.key_type),
            _types_conform(token, expression_type.value_type, expected_type.value_type)
        )
    elif isinstance(expression_type, SchemaType) and isinstance(expected_type, SchemaType):
        return expression_type
    elif isinstance(expression_type, TableType) and isinstance(expected_type, TableType):
        return expression_type
    elif isinstance(expression_type, LambdaType) and isinstance(expected_type, LambdaType):
        well_formed_parameter_types: List[PetlType] = _collection_types_conform(token,
                                                                                expression_type.parameter_types,
                                                                                expected_type.parameter_types)
        well_formed_return_type: PetlType = _types_conform(token, expression_type.return_type,
                                                                expected_type.return_type)
        return LambdaType(well_formed_parameter_types, well_formed_return_type)
    elif not isinstance(expression_type, UnknownType) and not isinstance(expected_type, UnknownType):
        if type(expression_type) is type(expected_type):
            return _make_well_formed(expression_type, token)
        else:
            return UnknownType()
    else:
        return UnknownType()


def types_conform(token: Token, expression_type: PetlType, expected_type: PetlType, logger: Log, no_error=False) -> Optional[PetlType]:
    conformed_type: PetlType = _types_conform(token, expression_type, expected_type)
    if not _is_well_formed(conformed_type):
        if not no_error:
            logger.error(f"Type mismatch: {expression_type.to_string()} vs. {expected_type.to_string()}\n{token.file_position.to_string()}")
        return None
    else:
        return conformed_type
