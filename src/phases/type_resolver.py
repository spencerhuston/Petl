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

    def add(self, identifier: str, value_type: PetlType):
        self.map[identifier] = value_type

    def add_alias(self, identifier: str, value_type: PetlType):
        self.aliases[identifier] = value_type

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

    def extract_iterable_type(self, collection_type: PetlType, token: Token, dict_value_type=False) -> Optional[PetlType]:
        if isinstance(collection_type, ListType):
            return collection_type.list_type
        elif isinstance(collection_type, TupleType):
            return UnionType(collection_type.tuple_types)
        elif isinstance(collection_type, DictType):
            return collection_type.value_type if dict_value_type else collection_type.key_type
        elif isinstance(collection_type, SchemaType):
            return UnionType(collection_type.column_types)
        elif isinstance(collection_type, TableType):
            return UnionType(collection_type.schema_type.column_types)
        else:
            self.logger.error(f"Non-iterable provided for iterator\n{token.file_position.to_string()}")
            return None

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
        elif isinstance(t, UnionType):
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
        elif isinstance(expression_type, AnyType) and not isinstance(expected_type, AnyType):
            return self.make_well_formed(expected_type, token)
        elif not isinstance(expression_type, AnyType) and isinstance(expected_type, AnyType):
            return self.make_well_formed(expression_type, token)
        elif isinstance(expression_type, UnionType) and isinstance(expected_type, UnionType):
            return UnionType(self.collection_types_conform(token, expression_type.union_types, expected_type.union_types, environment))
        elif isinstance(expression_type, UnionType) and not isinstance(expected_type, UnionType) and expected_type in expression_type.union_types:
            return self.make_well_formed(expected_type, token)
        elif not isinstance(expression_type, UnionType) and isinstance(expected_type, UnionType) and expression_type in expected_type.union_types:
            return self.make_well_formed(expression_type, token)
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

    def resolve_expression(self, root_expression: Expression) -> Optional[Expression]:
        well_formed_root_expression: Optional[Expression] = self.resolve(root_expression, TypeEnvironment(), UnknownType())
        if well_formed_root_expression:
            self.logger.debug_block("TYPED EXPRESSION", well_formed_root_expression.to_string())
        return well_formed_root_expression

    def resolve(self, expression: Expression, environment: TypeEnvironment, expected_type: PetlType) -> Optional[Expression]:
        if isinstance(expression, LitExpression):
            literal_type: PetlType = self.conform_types(expression.token, expression.petl_type, expected_type, environment)
            return LitExpression(literal_type, expression.token, expression.literal)
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
        else:
            return None

    def resolve_let(self, let: Let, environment: TypeEnvironment, expected_type: PetlType) -> Let:
        let_expression: Expression = self.resolve(let.let_expression, environment, let.let_type)
        let_environment: TypeEnvironment = copy(environment)
        let_environment.add(let.identifier, let_expression.petl_type)
        after_let_expression: Optional[Expression] = self.resolve(let.after_let_expression, let_environment, expected_type)
        let_type: PetlType = after_let_expression.petl_type if after_let_expression else NoneType()
        return Let(let_type, let.token, let.identifier, let_expression.petl_type, let_expression, after_let_expression)

    def resolve_alias(self, alias: Alias, environment: TypeEnvironment, expected_type: PetlType) -> Alias:
        alias_environment: TypeEnvironment = copy(environment)
        alias_environment.add_alias(alias.identifier, alias.alias_type)
        after_alias_expression: Expression = self.resolve(alias.after_alias_expression, alias_environment, expected_type)
        return Alias(after_alias_expression.petl_type, alias.token, alias.identifier, alias.alias_type, after_alias_expression)

    def resolve_lambda(self, lambda_expression: Lambda, environment: TypeEnvironment, expected_type: PetlType) -> Lambda:
        lambda_environment: TypeEnvironment = copy(environment)
        for parameter in lambda_expression.parameters:
            lambda_environment.add(parameter.identifier, parameter.parameter_type)
        body: Expression = self.resolve(lambda_expression.body, lambda_environment, lambda_expression.return_type)
        lambda_type: PetlType = self._conform_types(lambda_expression.token, lambda_expression.petl_type, expected_type, environment)
        return Lambda(lambda_type, lambda_expression.token, lambda_expression.parameters, lambda_expression.return_type, body)

    def resolve_application(self, application: Application, environment: TypeEnvironment, expected_type: PetlType) -> Application:
        token: Token = application.token
        typed_identifier: Expression = self.resolve(application.identifier, environment, UnknownType())
        arguments: List[Expression] = copy(application.arguments)
        if isinstance(typed_identifier.petl_type, LambdaType):
            well_formed_arguments: List[Expression] = []
            if len(arguments) != len(typed_identifier.petl_type.parameter_types):
                self.logger.error(f"Argument mismatch\n{token.file_position.to_string()}")
                return application
            zipped_args_param_types: List[Tuple[Expression, PetlType]] = list(map(lambda a, t: (a, t), arguments, typed_identifier.petl_type.parameter_types))
            for argument, parameter_type in zipped_args_param_types:
                well_formed_arguments.append(self.resolve(argument, environment, parameter_type))
            well_formed_return_type: PetlType = self.conform_types(token, typed_identifier.petl_type.return_type, expected_type, environment)
            return Application(well_formed_return_type, token, typed_identifier, well_formed_arguments)
        else:
            return self.resolve_collection_application(token, typed_identifier, arguments, environment, expected_type)

    def resolve_collection_application(self, token: Token, typed_identifier: Expression, arguments: List[Expression], environment: TypeEnvironment, expected_type: PetlType):
        if len(arguments) != 1:
            self.logger.error(f"Type \'{typed_identifier.petl_type}\' requires one integer argument")
            return typed_identifier
        argument: Expression = arguments[0]
        well_formed_argument: Expression = UnknownExpression()
        if isinstance(typed_identifier.petl_type, ListType):
            well_formed_argument = self.resolve(argument, environment, IntType())
        elif isinstance(typed_identifier.petl_type, DictType):
            well_formed_argument = self.resolve(argument, environment, typed_identifier.petl_type.key_type)
        elif isinstance(typed_identifier.petl_type, TupleType):
            well_formed_argument = self.resolve(argument, environment, IntType())
        elif isinstance(typed_identifier.petl_type, TableType):
            well_formed_argument = self.resolve(argument, environment, StringType())
        elif isinstance(typed_identifier.petl_type, UnionType):
            well_formed_argument = self.resolve(argument, environment, typed_identifier.petl_type)
        well_formed_type = self.conform_types(argument.token, self.extract_iterable_type(typed_identifier.petl_type, token, dict_value_type=True), expected_type, environment)
        return Application(well_formed_type, token, typed_identifier, [well_formed_argument])

    def resolve_match(self, match: Match, environment: TypeEnvironment, expected_type: PetlType) -> Match:
        pass

    def resolve_primitve(self, primitive: Primitive, environment: TypeEnvironment, expected_type: PetlType) -> Primitive:
        pass

    def resolve_reference(self, reference: Reference, environment: TypeEnvironment, expected_type: PetlType) -> Reference:
        reference_type: Optional[PetlType] = environment.get(reference.identifier, reference.token, self.logger)
        if reference_type:
            well_formed_reference_type: PetlType = self.conform_types(reference.token, reference_type, expected_type, environment)
            return Reference(well_formed_reference_type, reference.token, reference.identifier)

    def resolve_branch(self, branch: Branch, environment: TypeEnvironment, expected_type: PetlType) -> Branch:
        predicate: Expression = self.resolve(branch.predicate, environment, BoolType())
        else_branch: Expression = self.resolve(branch.else_branch, environment, expected_type)
        if_branch: Expression = self.resolve(branch.if_branch, environment, else_branch.petl_type)
        return Branch(else_branch.petl_type, branch.token, predicate, if_branch, else_branch)

    def resolve_for(self, for_expression: For, environment: TypeEnvironment, expected_type: PetlType) -> For:
        iterable_expression: Expression = self.resolve(for_expression.iterable, environment, UnknownType())
        iterable_type: Optional[Union[PetlType, List[PetlType]]] = self.extract_iterable_type(iterable_expression.petl_type, for_expression.token)
        if iterable_type:
            for_environment: TypeEnvironment = copy(environment)
            for_environment.add(for_expression.reference, iterable_type) # TODO
            body: Expression = self.resolve(for_expression.body, for_environment, UnknownType())
            after_for_expression: Optional[Expression] = self.resolve(for_expression.after_for_expression, for_environment, expected_type)
            for_type: PetlType = after_for_expression.petl_type if after_for_expression else NoneType()
            return For(for_type, for_expression.token, for_expression.reference, iterable_expression, body, after_for_expression)
        else:
            return for_expression

    def resolve_list_definition(self, list_definition: ListDefinition, environment: TypeEnvironment, expected_type: PetlType) -> ListDefinition:
        token = list_definition.token
        if isinstance(list_definition.petl_type, ListType):
            list_element_type: PetlType = list_definition.petl_type.list_type
            values_well_formed: List[Expression] = list(map(lambda v: self.resolve(v, environment, list_element_type), list_definition.values))
            list_type: PetlType = ListType(values_well_formed[0].petl_type if values_well_formed else UnknownType())
            well_formed_list_type: PetlType = self.conform_types(list_definition.token, list_type, expected_type, environment)
            return ListDefinition(well_formed_list_type, token, list_definition.values)
        else:
            return list_definition

    def resolve_range_definition(self, range_definition: RangeDefinition, environment: TypeEnvironment, expected_type: PetlType) -> RangeDefinition:
        token = range_definition.token
        well_formed_range_type: PetlType = self.conform_types(token, range_definition.petl_type, ListType(IntType()), environment)
        well_formed_range_type = self.conform_types(token, well_formed_range_type, expected_type, environment)
        if isinstance(range_definition.start, IntLiteral) and isinstance(range_definition.end, IntLiteral):
            return RangeDefinition(well_formed_range_type, token, range_definition.start, range_definition.end)
        else:
            self.logger.error("Range definition supports only integer type")
            return range_definition

    def resolve_tuple_definition(self, tuple_definition: TupleDefinition, environment: TypeEnvironment, expected_type: PetlType) -> TupleDefinition:
        token = tuple_definition.token
        if isinstance(tuple_definition.petl_type, TupleType):
            tuple_type_well_formed: PetlType = self.conform_types(token, tuple_definition.petl_type, expected_type, environment)
            if isinstance(tuple_type_well_formed, TupleType):
                well_formed_values: List[Expression] = list(map(
                    lambda v, tt: self.resolve(v, environment, tt),
                    tuple_definition.values,
                    tuple_type_well_formed.tuple_types)
                )
                return TupleDefinition(tuple_type_well_formed, token, well_formed_values)
        return tuple_definition

    def resolve_dict_definition(self, dict_definition: DictDefinition, environment: TypeEnvironment, expected_type: PetlType) -> DictDefinition:
        token = dict_definition.token
        if isinstance(dict_definition.petl_type, DictType):
            pass
        else:
            return dict_definition

    def resolve_schema_definition(self, schema_definition: SchemaDefinition, environment: TypeEnvironment, expected_type: PetlType) -> SchemaDefinition:
        token = schema_definition.token
        if isinstance(schema_definition.petl_type, SchemaType):
            pass
        else:
            return schema_definition
