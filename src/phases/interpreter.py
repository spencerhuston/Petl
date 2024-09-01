from copy import copy

from src.phases.environment import InterpreterEnvironment
from src.phases.petl_phase import PetlPhase
from src.phases.type_resolver import types_conform
from src.semantic_defintions.petl_expression import *
from src.semantic_defintions.petl_value import *


class Interpreter(PetlPhase):
    def __init__(self, debug=False):
        self.logger.__init__(debug)
        self.environment = InterpreterEnvironment()

    def interpret(self, root_expression):
        self.evaluate(root_expression, InterpreterEnvironment(), AnyType())

    def evaluate(self, expression: Expression, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if isinstance(expression, LitExpression):
            return self.evaluate_literal(expression, expected_type)
        elif isinstance(expression, Let):
            return self.evaluate_let(expression, environment, expected_type)
        elif isinstance(expression, Alias):
            return self.evaluate_alias(expression, environment, expected_type)
        elif isinstance(expression, Lambda):
            return self.evaluate_lambda(expression, environment, expected_type)
        elif isinstance(expression, Application):
            return self.evaluate_application(expression, environment, expected_type)
        elif isinstance(expression, Match):
            return self.evaluate_match(expression, environment, expected_type)
        elif isinstance(expression, Primitive):
            return self.evaluate_primitve(expression, environment, expected_type)
        elif isinstance(expression, Reference):
            return self.evaluate_reference(expression, environment, expected_type)
        elif isinstance(expression, Branch):
            return self.evaluate_branch(expression, environment, expected_type)
        elif isinstance(expression, For):
            return self.evaluate_for(expression, environment, expected_type)
        elif isinstance(expression, ListDefinition):
            return self.evaluate_list_definition(expression, environment, expected_type)
        elif isinstance(expression, RangeDefinition):
            return self.evaluate_range_definition(expression, expected_type)
        elif isinstance(expression, TupleDefinition):
            return self.evaluate_tuple_definition(expression, environment, expected_type)
        elif isinstance(expression, DictDefinition):
            return self.evaluate_dict_definition(expression, environment, expected_type)
        elif isinstance(expression, SchemaDefinition):
            return self.evaluate_schema_definition(expression, environment, expected_type)
        else:
            self.logger.error(f"Invalid expression found\n{expression.token.file_position.to_string()}")
            return NoneValue()

    def evaluate_literal(self, literal_expression: LitExpression, expected_type: PetlType) -> PetlValue:
        if types_conform(literal_expression.token, literal_expression.petl_type, expected_type, self.logger):
            if isinstance(literal_expression.literal, IntLiteral):
                return IntValue(literal_expression.literal.value)
            elif isinstance(literal_expression.literal, BoolLiteral):
                return BoolValue(literal_expression.literal.value)
            elif isinstance(literal_expression.literal, CharLiteral):
                return CharValue(literal_expression.literal.value)
            elif isinstance(literal_expression.literal, StringLiteral):
                return StringValue(literal_expression.literal.value)
            elif isinstance(literal_expression.literal, NoneLiteral):
                return NoneValue()
        self.logger.error(f"Invalid expression found\n{literal_expression.token.to_string()}")

    def evaluate_let(self, let: Let, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        let_value: PetlValue = self.evaluate(let.let_expression, environment, let.let_type)
        after_let_environment = copy(environment)
        after_let_environment.add(let.identifier, let_value)
        if let.after_let_expression:
            return self.evaluate(let.after_let_expression, after_let_environment, expected_type)
        else:
            return NoneValue()

    def evaluate_alias(self, alias: Alias, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if alias.after_alias_expression:
            after_alias_environment = copy(environment)
            after_alias_environment.add_alias(alias.identifier, alias.alias_type)
            return self.evaluate(alias.after_alias_expression, after_alias_environment, expected_type)
        else:
            return NoneValue()

    def evaluate_lambda(self, lambda_expression: Lambda, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if types_conform(lambda_expression.token, lambda_expression.petl_type, expected_type, self.logger):
            parameters: List[Tuple[str, PetlType]] = list(map(lambda p: (p.identifier, p.parameter_type), lambda_expression.parameters))
            return LambdaValue(False, parameters, copy(lambda_expression.body), copy(environment))
        else:
            return NoneValue()

    def evaluate_application(self, application: Application, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        identifier: PetlValue = self.evaluate(application.identifier, environment, UnknownType())
        if isinstance(identifier, LambdaValue):
            return self.evaluate_lambda_application(application, identifier, environment, expected_type)
        elif isinstance(identifier, StringValue):
            return self.evaluate_string_application(application, identifier, environment, expected_type)
        elif isinstance(identifier, ListValue):
            return self.evaluate_list_application(application, identifier, environment, expected_type)
        elif isinstance(identifier, TupleValue):
            return self.evaluate_tuple_application(application, identifier, environment, expected_type)
        elif isinstance(identifier, DictValue):
            return self.evaluate_dict_application(application, identifier, environment, expected_type)
        else:
            self.logger.error(f"Invalid type for application: {identifier.petl_type.to_string()}\n{application.token.file_position.to_string()}")

    def evaluate_lambda_application(self, application: Application, identifier: LambdaValue, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if len(application.arguments) != len(identifier.parameters):
            self.logger.error(f"Invalid argument count for lambda\n{application.token.file_position.to_string()}")
            return NoneValue()

        lambda_environment: InterpreterEnvironment = copy(environment)
        for argument, parameter in application.arguments, identifier.parameters:
            lambda_environment.add(parameter.identifier, self.evaluate(argument, environment, parameter.parameter_type))

        lambda_return_value: PetlValue = NoneValue()
        if isinstance(identifier.petl_type, LambdaType):
            if identifier.builtin:

            else:
                lambda_return_value = self.evaluate(identifier.body, lambda_environment, identifier.petl_type.return_type)
            types_conform(application.token, lambda_return_value.petl_type, expected_type, self.logger)

        return lambda_return_value

    def evaluate_string_application(self, application: Application, identifier: StringValue, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if len(application.arguments) != 1:
            self.logger.error(f"Argument count must be 1 for string access\n{application.token.file_position.to_string()}")
            return NoneValue()

        argument_value: PetlValue = self.evaluate(application.arguments[0], environment, IntType())
        if isinstance(argument_value, IntValue):
            if argument_value.value < 0 or argument_value.value >= len(identifier.value):
                self.logger.error(f"Invalid argument value for string access\n{application.token.file_position.to_string()}")
                return NoneValue()
            element_value: PetlValue = CharValue(identifier.value[argument_value.value])
            if types_conform(application.token, element_value.petl_type, expected_type, self.logger):
                return element_value
        return NoneValue()

    def evaluate_list_application(self, application: Application, identifier: ListValue, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if len(application.arguments) != 1:
            self.logger.error(f"Argument count must be 1 for list access\n{application.token.file_position.to_string()}")
            return NoneValue()

        argument_value: PetlValue = self.evaluate(application.arguments[0], environment, IntType())
        if isinstance(argument_value, IntValue):
            if argument_value.value < 0 or argument_value.value >= len(identifier.values):
                self.logger.error(f"Invalid argument value for list access\n{application.token.file_position.to_string()}")
                return NoneValue()
            element_value: PetlValue = identifier.values[argument_value.value]
            if types_conform(application.token, element_value.petl_type, expected_type, self.logger):
                return element_value
        return NoneValue()

    def evaluate_tuple_application(self, application: Application, identifier: TupleValue, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if len(application.arguments) != 1:
            self.logger.error(f"Argument count must be 1 for tuple access\n{application.token.file_position.to_string()}")
            return NoneValue()

        argument_value: PetlValue = self.evaluate(application.arguments[0], environment, IntType())
        if isinstance(argument_value, IntValue):
            if argument_value.value < 0 or argument_value.value >= len(identifier.values):
                self.logger.error(f"Invalid argument value for tuple access\n{application.token.file_position.to_string()}")
                return NoneValue()
            element_value: PetlValue = identifier.values[argument_value.value]
            if types_conform(application.token, element_value.petl_type, expected_type, self.logger):
                return element_value
        return NoneValue()

    def evaluate_dict_application(self, application: Application, identifier: DictValue, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if len(application.arguments) != 1:
            self.logger.error(f"Argument count must be 1 for dictionary access\n{application.token.file_position.to_string()}")
            return NoneValue()

        if isinstance(identifier.petl_type, DictType):
            argument_value: PetlValue = self.evaluate(application.arguments[0], environment, identifier.petl_type.key_type)

            values: List[PetlValue] = list(filter(lambda v: values_equal(v[0], argument_value), identifier.values))
            if len(values) == 1 and types_conform(application.token, values[0].petl_type, expected_type, self.logger):
                return values[0]
            else:
                self.logger.error(f"Key does not exist in dictionary\n{application.arguments[0].token.file_position.to_string()}")
        return NoneValue()

    def evaluate_match(self, match: Match, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        pass

    def evaluate_primitve(self, primitive: Primitive, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        pass

    def evaluate_reference(self, reference: Reference, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        reference_value: PetlValue = environment.get(reference.identifier, reference.token, self.logger)
        if types_conform(reference.token, reference_value.petl_type, expected_type, self.logger):
            return reference_value
        else:
            return NoneValue()

    def evaluate_branch(self, branch: Branch, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        predicate_value: PetlValue = self.evaluate(branch.predicate, environment, BoolType())
        if isinstance(predicate_value, BoolValue):
            if predicate_value.value:
                return self.evaluate(branch.if_branch, environment, expected_type)
            else:
                return self.evaluate(branch.else_branch, environment, expected_type)
        return NoneValue()

    def evaluate_for(self, for_expression: For, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        pass

    def evaluate_list_definition(self, list_definition: ListDefinition, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if isinstance(list_definition.petl_type, ListType):
            element_type: PetlType = list_definition.petl_type.list_type
            list_values: List[PetlValue] = list(map(lambda v: self.evaluate(v, environment, element_type), list_definition.values))
            if list_values and all(map(lambda v: types_conform(list_definition.token, v.petl_types, list_values[0].petl_type, self.logger), list_values)):
                element_type = list_values[0].petl_type
            else:
                element_type = UnknownType()
            list_type: PetlType = types_conform(list_definition.token, ListType(element_type), expected_type, self.logger)
            if list_type:
                return ListValue(list_type, list_values)
        return NoneValue()

    def evaluate_range_definition(self, range_definition: RangeDefinition, expected_type: PetlType) -> PetlValue:
        if isinstance(range_definition.start, IntLiteral) and isinstance(range_definition.end, IntLiteral):
            start_value: int = range_definition.start.value
            end_value: int = range_definition.end.value
            if start_value < 0 or end_value < 0:
                self.logger.error(f"Range bounds cannot be negative\n{range_definition.token.file_position.to_string()}")
            elif types_conform(range_definition.token, ListType(IntType()), expected_type, self.logger):
                return ListValue(ListType(IntType()), list(map(lambda l: IntValue(l), range(start_value, end_value))))
        return NoneValue()

    def evaluate_tuple_definition(self, tuple_definition: TupleDefinition, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if isinstance(tuple_definition.petl_type, TupleType):
            tuple_element_types: List[PetlType] = tuple_definition.petl_type.tuple_types
            if types_conform(tuple_definition.token, tuple_definition.petl_type, expected_type, self.logger):
                tuple_values: List[PetlValue] = list(map(lambda tv, tet: self.evaluate(tv, environment, tet), tuple_definition.values, tuple_element_types))
                return TupleValue(tuple_definition.petl_type, tuple_values)
            return NoneValue()

    def evaluate_dict_definition(self, dict_definition: DictDefinition, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        def literal_to_expression(literal: Literal) -> Expression:
            if isinstance(literal, IntLiteral):
                return LitExpression(IntType(), dict_definition.token, literal)
            elif isinstance(literal, BoolLiteral):
                return LitExpression(BoolType(), dict_definition.token, literal)
            elif isinstance(literal, CharLiteral):
                return LitExpression(CharType(), dict_definition.token, literal)
            elif isinstance(literal, StringLiteral):
                return LitExpression(StringType(), dict_definition.token, literal)
            else:
                self.logger.error(f"Invalid dictionary key type\n{dict_definition.token.file_position.to_string()}")
                return LitExpression(NoneType(), dict_definition.token, NoneLiteral())

        def all_types_align(dict_values: List[Tuple[PetlValue, PetlValue]]) -> bool:
            return dict_values and \
                   all(map(lambda v: types_conform(dict_definition.token, v[0], dict_values[0][0].petl_type, self.logger), dict_values)) and \
                   all(map(lambda v: types_conform(dict_definition.token, v[1], dict_values[0][1].petl_type, self.logger), dict_values))

        if isinstance(dict_definition.petl_type, DictType):
            key_type: PetlType = dict_definition.petl_type.key_type
            entry_key_values: List[PetlValue] = list(map(lambda entry: self.evaluate(literal_to_expression(entry[0]), environment, key_type), dict_definition.mapping))
            value_type: PetlType = dict_definition.petl_type.value_type
            entry_values: List[PetlValue] = list(map(lambda entry: self.evaluate(entry[1], environment, value_type), dict_definition.mapping))
            dict_values: List[Tuple[PetlValue, PetlValue]] = list(map(lambda k, v: (k, v), entry_key_values, entry_values))
            if all_types_align(dict_values):
                key_type = dict_values[0][0].petl_type
                value_type = dict_values[0][1].petl_type
            else:
                key_type = UnknownType()
                value_type = UnknownType()
            dict_type: PetlType = types_conform(dict_definition.token, DictType(key_type, value_type), expected_type, self.logger)
            if dict_type:
                return DictValue(dict_type, dict_values)
        return NoneValue()

    def evaluate_schema_definition(self, schema_definition: SchemaDefinition, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        pass
