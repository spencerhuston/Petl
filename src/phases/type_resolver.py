from copy import copy
from typing import Dict

from src.phases.petl_phase import PetlPhase
from src.semantic_defintions.petl_expression import *
from src.semantic_defintions.petl_types import *
from src.tokens.petl_token import Token
from src.utils.log import Log


class TypeEnvironment:
    map: Dict[str, PetlType] = {}
    aliases: Dict[str, PetlType] = {}

    def add(self, identifier: str, value_type: PetlType) -> Self:
        self.map[identifier] = value_type
        return self

    def add_alias(self, identifier: str, value_type: PetlType) -> Self:
        self.aliases[identifier] = value_type
        return self

    def get(self, identifier: str, token: Token, logger: Log) -> Optional[PetlType]:
        if identifier in self.map:
            return self.map[identifier]
        elif identifier in self.aliases:
            return self.aliases[identifier]
        else:
            logger.error(f"Identifier {identifier} does not exist in this scope\n{token.file_position.to_string()}")
            return None

class TypeResolver(PetlPhase):
    def __init__(self, debug=False):
        self.logger.__init__(debug)

    def make_well_formed(self, t: PetlType, token: Token) -> PetlType:
        if isinstance(t, UnionType):
            return UnionType(list(map(lambda ut: self.make_well_formed(ut, token), t.union_types)))
        elif isinstance(t, ListType):
            return ListType(self.make_well_formed(t.list_type, token))
        elif isinstance(t, TupleType):
            return TupleType(list(map(lambda tt: self.make_well_formed(tt, token), t.tuple_types)))
        elif isinstance(t, DictType):
            return DictType(self.make_well_formed(t.key_type, token), self.make_well_formed(t.value_type, token))
        elif isinstance(t, SchemaType):
            return SchemaType(list(map(lambda st: self.make_well_formed(st, token), t.column_types)))
        elif isinstance(t, TableType):
            return TableType(SchemaType(list(map(lambda st: self.make_well_formed(st, token), t.schema_type.column_types))))
        elif isinstance(t, LambdaType):
            return LambdaType(list(map(lambda pt: self.make_well_formed(pt, token), t.parameter_types)), self.make_well_formed(t.return_type, token))
        elif not isinstance(t, UnknownType):
            return t
        else:
            self.logger.error(f"Cannot deduce unknown type\n{token.file_position.to_string()}")
            return t

    def is_well_formed(self, t: PetlType) -> bool:
        if isinstance(t, UnknownType):
            return False
        elif isinstance(t, UnionType)
            return all(map(lambda ut: self.is_well_formed(ut), t.union_types))
        elif isinstance(t, ListType):
            return self.is_well_formed(t.list_type)
        elif isinstance(t, TupleType):
            return all(map(lambda tt: self.is_well_formed(tt), t.tuple_types))
        elif isinstance(t, DictType):
            return self.is_well_formed(t.key_type) and self.is_well_formed(t.value_type)
        elif isinstance(t, SchemaType):
            return all(map(lambda st: self.is_well_formed(st), t.column_types))
        elif isinstance(t, TableType):
            return all(map(lambda tct: self.is_well_formed(tct), t.schema_type.column_types))
        elif isinstance(t, LambdaType):
            return all(map(lambda pt: self.is_well_formed(pt), t.parameter_types)) and self.is_well_formed(t.return_type)
        else:
            return True


    def collection_types_conform(self, token: Token, expression_type_list: List[PetlType], expected_type_list: List[PetlType], environment: TypeEnvironment) -> List[PetlType]:
        zipped_types: List[Tuple[PetlType, PetlType]] = list(map(lambda t1, t2: (t1, t2), expression_type_list, expected_type_list))
        return list(map(lambda t: self._conform_types(token, t[0], t[1], environment), zipped_types))

    def _conform_types(self, token: Token, expression_type: PetlType, expected_type: PetlType, environment: TypeEnvironment) -> PetlType:
        if not isinstance(expression_type, UnknownType) and isinstance(expected_type, UnknownType):
            return self.make_well_formed(expression_type, token)
        elif isinstance(expression_type, UnknownType) and not isinstance(expected_type, UnknownType):
            return self.make_well_formed(expected_type, token)
        if isinstance(expression_type, UnionType) and isinstance(expected_type, UnionType):
            return UnionType(self.collection_types_conform(token, expression_type.union_types, expected_type.union_types, environment))
        elif isinstance(expression_type, ListType) and isinstance(expected_type, ListType):
            return ListType(self._conform_types(token, expression_type.list_type, expected_type.list_type, environment))
        elif isinstance(expression_type, TupleType) and isinstance(expected_type, TupleType) and expression_type.tuple_types and expected_type.tuple_types:
            return TupleType(self.collection_types_conform(token, expression_type.tuple_types, expected_type.tuple_types, environment))
        elif isinstance(expression_type, DictType) and isinstance(expected_type, DictType):
            return DictType(
                self._conform_types(token, expression_type.key_type, expected_type.key_type, environment),
                self._conform_types(token, expression_type.value_type, expected_type.value_type, environment)
            )
        elif isinstance(expression_type, SchemaType) and isinstance(expected_type, SchemaType):
            return SchemaType(self.collection_types_conform(token, expression_type.column_types, expected_type.column_types, environment))
        elif isinstance(expression_type, TableType) and isinstance(expected_type, TableType):
            return TableType(SchemaType(
                self.collection_types_conform(token, expression_type.schema_type.column_types, expected_type.schema_type.column_types, environment))
            )
        elif isinstance(expression_type, LambdaType) and isinstance(expected_type, LambdaType):
            well_formed_parameter_types: List[PetlType] = self.collection_types_conform(token, expression_type.parameter_types, expected_type.parameter_types, environment)
            well_formed_return_type: PetlType = self._conform_types(token, expression_type.return_type, expected_type.return_type, environment)
            return LambdaType(well_formed_parameter_types, well_formed_return_type)
        elif not isinstance(expression_type, UnknownType) and not isinstance(expected_type, UnknownType):
            if type(expression_type) is type(expected_type):
                return self.make_well_formed(expression_type, token)
            else:
                return UnknownType()
        else:
            return UnknownType()

    def conform_types(self, token: Token, expression_type: PetlType, expected_type: PetlType, environment: TypeEnvironment) -> PetlType:
        conformed_type: PetlType = self._conform_types(token, expression_type, expected_type, environment)
        if not self.is_well_formed(conformed_type):
            self.logger.error(f"Type mismatch: {expression_type.to_string()} vs. {expected_type.to_string()}\n{token.file_position.to_string()}")
            return UnknownType()
        else:
            return conformed_type

    def resolve_expression(self, root_expression: Expression) -> Expression:
        return self.resolve(root_expression, TypeEnvironment(), UnknownType())

    def resolve(self, expression: Expression, environment: TypeEnvironment, expected_type: PetlType) -> Expression:
        if isinstance(expression, LitExpression):
            return expression.using_type(self._conform_types(expression.token, expression.petl_type, expected_type, environment))
        elif isinstance(expression, Let):
            return self.resolve_let(expression, environment, expected_type)
        elif isinstance(expression, Alias):
            return self.resolve_alias(expression, environment, expected_type)
        elif isinstance(expression, Lambda):
            return self.resolve_lambda(expression, environment, expected_type)
        elif isinstance(expression, Application):
            return self.resolve_application(expression, environment, expected_type)
        elif isinstance(expression, Match):
            return self.resolve_match(expression, environment, expected_type)
        elif isinstance(expression, Primitive):
            return self.resolve_primitve(expression, environment, expected_type)
        elif isinstance(expression, Reference):
            return self.resolve_reference(expression, environment, expected_type)
        elif isinstance(expression, Branch):
            return self.resolve_branch(expression, environment, expected_type)
        elif isinstance(expression, For):
            return self.resolve_for(expression, environment, expected_type)
        elif isinstance(expression, ListDefinition):
            return self.resolve_list_definition(expression, environment, expected_type)
        elif isinstance(expression, RangeDefinition):
            return self.resolve_range_definition(expression, environment, expected_type)
        elif isinstance(expression, TupleDefinition):
            return self.resolve_tuple_definition(expression, environment, expected_type)
        elif isinstance(expression, DictDefinition):
            return self.resolve_dict_definition(expression, environment, expected_type)
        elif isinstance(expression, SchemaDefinition):
            return self.resolve_schema_definition(expression, environment, expected_type)

    def resolve_let(self, let: Let, environment: TypeEnvironment, expected_type: PetlType) -> Let:
        let_expression: Expression = self.resolve(let.let_expression, environment, let.let_type)
        after_let_expression: Expression = self.resolve(let.after_let_expression, environment.add(let.identifier, let.let_type), expected_type)
        return Let(after_let_expression.petl_type, let.token, let.identifier, let_expression.petl_type, let_expression, after_let_expression)

    def resolve_alias(self, alias: Alias, environment: TypeEnvironment, expected_type: PetlType) -> Alias:
        after_alias_expression: Expression = self.resolve(alias.after_alias_expression, environment.add_alias(alias.identifier, alias.alias_type), expected_type)
        return Alias(after_alias_expression.petl_type, alias.token, alias.identifier, alias.alias_type, after_alias_expression)

    def resolve_lambda(self, lambda_expression: Lambda, environment: TypeEnvironment, expected_type: PetlType) -> Lambda:
        lambda_environment: TypeEnvironment = copy(environment)
        for parameter in lambda_expression.parameters:
            lambda_environment = lambda_environment.add(parameter.identifier, parameter.parameter_type)
        body: Expression = self.resolve(lambda_expression.body, lambda_environment, lambda_expression.return_type)
        lambda_type: PetlType = self._conform_types(lambda_expression.token, lambda_expression.petl_type, expected_type, environment)
        return Lambda(lambda_type, lambda_expression.token, lambda_expression.parameters, lambda_expression.return_type, body)

    def resolve_application(self, application: Application, environment: TypeEnvironment, expected_type: PetlType) -> Application:
        pass

    def resolve_match(self, match: Match, environment: TypeEnvironment, expected_type: PetlType) -> Match:
        pass

    def resolve_primitve(self, primitive: Primitive, environment: TypeEnvironment, expected_type: PetlType) -> Primitive:
        pass

    def resolve_reference(self, reference: Reference, environment: TypeEnvironment, expected_type: PetlType) -> Reference:
        pass

    def resolve_branch(self, branch: Branch, environment: TypeEnvironment, expected_type: PetlType) -> Branch:
        pass

    def resolve_for(self, for_expression: For, environment: TypeEnvironment, expected_type: PetlType) -> For:
        pass

    def resolve_list_definition(self, list_definition: ListDefinition, environment: TypeEnvironment, expected_type: PetlType) -> ListDefinition:
        pass

    def resolve_range_definition(self, range_definition: RangeDefinition, environment: TypeEnvironment, expected_type: PetlType) -> RangeDefinition:
        pass

    def resolve_tuple_definition(self, tuple_definition: TupleDefinition, environment: TypeEnvironment, expected_type: PetlType) -> TupleDefinition:
        pass

    def resolve_dict_definition(self, dict_definition: DictDefinition, environment: TypeEnvironment, expected_type: PetlType) -> DictDefinition:
        pass

    def resolve_schema_definition(self, schema_definition: SchemaDefinition, environment: TypeEnvironment, expected_type: PetlType) -> SchemaDefinition:
        pass