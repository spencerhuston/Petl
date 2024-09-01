import traceback
from copy import copy
from typing import Set

from src.builtins.petl_builtins import Builtin
from src.phases.environment import InterpreterEnvironment
from src.phases.petl_phase import PetlPhase
from src.phases.type_resolver import types_conform
from src.semantic_defintions.petl_expression import *
from src.semantic_defintions.petl_value import *
from src.utils.file_position import FilePosition


def load_builtins(builtins: Set[Builtin]) -> InterpreterEnvironment:
    environment: InterpreterEnvironment = InterpreterEnvironment()
    if builtins:
        for builtin in builtins:
            environment.add(builtin.name, builtin.to_value())
    return environment


class InterpreterException(Exception):
    pass


class Interpreter(PetlPhase):
    def __init__(self, debug=False):
        self.logger.__init__(debug)
        self.environment = InterpreterEnvironment()
        self.stack_trace: List[FilePosition] = []

    def error(self, text: str, token: Optional[Token] = None):
        if not self.stack_trace or (self.stack_trace and self.stack_trace[-1] != token.file_position):
            self.stack_trace.append(token.file_position)
        stack_trace_strs: List[str] = list(map(lambda fp: fp.to_string(), list(reversed(self.stack_trace))))
        stack_trace_str: Optional[str] = "" if not stack_trace_strs else functools.reduce(lambda fp1, fp2: f"{fp1}\n\tin\n{fp2}", stack_trace_strs)
        self.logger.error(f"{text}\n{stack_trace_str}")
        raise InterpreterException

    def literal_to_value(self, token: Token, literal: Literal) -> PetlValue:
        if isinstance(literal, IntLiteral):
            return IntValue(literal.value)
        elif isinstance(literal, BoolLiteral):
            return BoolValue(literal.value)
        if isinstance(literal, CharLiteral):
            return CharValue(literal.value)
        elif isinstance(literal, StringLiteral):
            return StringValue(literal.value)
        elif isinstance(literal, NoneLiteral):
            return NoneValue()
        else:
            self.error(f"Invalid type for pattern matching on literal value", token)
            return NoneValue()

    def interpret(self, root: Expression, environment: InterpreterEnvironment) -> PetlValue:
        try:
            return self.evaluate(root, environment, AnyType())
        except InterpreterException as ie:
            return NoneValue()
        except Exception as e:
            self.logger.error(f"Unhandled exception while interpreting: {e}, {traceback.format_exc()}")
            return NoneValue()

    def evaluate(self, expression: Expression, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        evaluated_value: PetlValue = NoneValue()
        if isinstance(expression, LitExpression):
            evaluated_value = self.evaluate_literal(expression, expected_type)
        elif isinstance(expression, Let):
            evaluated_value = self.evaluate_let(expression, environment, expected_type)
        elif isinstance(expression, Alias):
            evaluated_value = self.evaluate_alias(expression, environment, expected_type)
        elif isinstance(expression, Lambda):
            evaluated_value = self.evaluate_lambda(expression, environment, expected_type)
        elif isinstance(expression, Application):
            evaluated_value = self.evaluate_application(expression, environment, expected_type)
        elif isinstance(expression, Match):
            evaluated_value = self.evaluate_match(expression, environment, expected_type)
        elif isinstance(expression, Primitive):
            evaluated_value = self.evaluate_primitve(expression, environment, expected_type)
        elif isinstance(expression, Reference):
            evaluated_value = self.evaluate_reference(expression, environment, expected_type)
        elif isinstance(expression, Branch):
            evaluated_value = self.evaluate_branch(expression, environment, expected_type)
        elif isinstance(expression, For):
            evaluated_value = self.evaluate_for(expression, environment, expected_type)
        elif isinstance(expression, ListDefinition):
            evaluated_value = self.evaluate_list_definition(expression, environment, expected_type)
        elif isinstance(expression, RangeDefinition):
            evaluated_value = self.evaluate_range_definition(expression, expected_type)
        elif isinstance(expression, TupleDefinition):
            evaluated_value = self.evaluate_tuple_definition(expression, environment, expected_type)
        elif isinstance(expression, DictDefinition):
            evaluated_value = self.evaluate_dict_definition(expression, environment, expected_type)
        elif isinstance(expression, SchemaDefinition):
            evaluated_value = self.evaluate_schema_definition(expression, expected_type)
        else:
            self.error(f"Invalid expression found", expression.token)
        return evaluated_value

    def evaluate_literal(self, literal_expression: LitExpression, expected_type: PetlType) -> PetlValue:
        if types_conform(literal_expression.token, literal_expression.petl_type, expected_type, self.error):
            if isinstance(literal_expression.literal, IntLiteral):
                return IntValue(int(literal_expression.literal.value))
            elif isinstance(literal_expression.literal, BoolLiteral):
                return BoolValue(literal_expression.literal.value)
            elif isinstance(literal_expression.literal, CharLiteral):
                return CharValue(literal_expression.literal.value)
            elif isinstance(literal_expression.literal, StringLiteral):
                return StringValue(literal_expression.literal.value)
            elif isinstance(literal_expression.literal, NoneLiteral):
                return NoneValue()
        self.error(f"Invalid expression found", literal_expression.token)
        return NoneValue()

    def evaluate_let(self, let: Let, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        let_value: PetlValue = self.evaluate(let.let_expression, environment, let.let_type)
        unpacked_values: List[Tuple[str, PetlValue]] = [(let.identifiers[0], let_value)]
        if len(let.identifiers) > 1 and isinstance(let_value, TupleValue):
            unpacked_values = list(map(lambda i, v: (i, v), let.identifiers, let_value.values))
        elif len(let.identifiers) > 1 and not isinstance(let_value, TupleValue):
            self.error(f"Cannot unpack, requires tuple value", let.token)
            return NoneValue()

        after_let_environment = copy(environment)
        for unpacked_value in unpacked_values:
            after_let_environment.add(unpacked_value[0], unpacked_value[1])

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
        if types_conform(lambda_expression.token, lambda_expression.petl_type, expected_type, self.error):
            parameters: List[Tuple[str, PetlType]] = list(map(lambda p: (p.identifier, p.parameter_type), lambda_expression.parameters))
            return LambdaValue(lambda_expression.petl_type, "", parameters, copy(lambda_expression.body), copy(environment))
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
            self.error(f"Invalid type for application: {identifier.petl_type.to_string()}", application.token)

    def evaluate_lambda_application(self, application: Application, identifier: LambdaValue, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if len(application.arguments) != len(identifier.parameters):
            self.error(f"Invalid argument count for lambda", application.token)
            return NoneValue()

        lambda_environment: InterpreterEnvironment = copy(environment)
        argument_values: List[PetlValue] = []
        for argument, parameter in list(map(lambda a, p: (a, p), application.arguments, identifier.parameters)):
            argument_value: PetlValue = self.evaluate(argument, environment, parameter[1])
            lambda_environment.add(parameter[0], argument_value)
            argument_values.append(argument_value)

        lambda_return_value: PetlValue = NoneValue()
        if isinstance(identifier.petl_type, LambdaType):
            self.stack_trace.append(application.token.file_position)
            if identifier.builtin:
                lambda_return_value = identifier.builtin.evaluate(argument_values, lambda_environment, self.error)
            else:
                lambda_return_value = self.evaluate(identifier.body, lambda_environment, identifier.petl_type.return_type)
            types_conform(application.token, lambda_return_value.petl_type, expected_type, self.error)
            self.stack_trace.pop()

        return lambda_return_value

    def evaluate_string_application(self, application: Application, identifier: StringValue, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if len(application.arguments) != 1:
            self.error(f"Argument count must be 1 for string access", application.token)
            return NoneValue()

        argument_value: PetlValue = self.evaluate(application.arguments[0], environment, IntType())
        if isinstance(argument_value, IntValue):
            if argument_value.value < 0 or argument_value.value >= len(identifier.value):
                self.error(f"Invalid argument value for string access", application.token)
                return NoneValue()
            element_value: PetlValue = CharValue(identifier.value[argument_value.value])
            if types_conform(application.token, element_value.petl_type, expected_type, self.error):
                return element_value
        return NoneValue()

    def evaluate_list_application(self, application: Application, identifier: ListValue, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if len(application.arguments) != 1:
            self.error(f"Argument count must be 1 for list access", application.token)
            return NoneValue()

        argument_value: PetlValue = self.evaluate(application.arguments[0], environment, IntType())
        if isinstance(argument_value, IntValue):
            if argument_value.value < 0 or argument_value.value >= len(identifier.values):
                self.error(f"Invalid argument value for list access", application.token)
                return NoneValue()
            element_value: PetlValue = identifier.values[argument_value.value]
            if types_conform(application.token, element_value.petl_type, expected_type, self.error):
                return element_value
        return NoneValue()

    def evaluate_tuple_application(self, application: Application, identifier: TupleValue, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if len(application.arguments) != 1:
            self.error(f"Argument count must be 1 for tuple access", application.token)
            return NoneValue()

        argument_value: PetlValue = self.evaluate(application.arguments[0], environment, IntType())
        if isinstance(argument_value, IntValue):
            if argument_value.value < 0 or argument_value.value >= len(identifier.values):
                self.error(f"Invalid argument value for tuple access", application.token)
                return NoneValue()
            element_value: PetlValue = identifier.values[argument_value.value]
            if types_conform(application.token, element_value.petl_type, expected_type, self.error):
                return element_value
        return NoneValue()

    def evaluate_dict_application(self, application: Application, identifier: DictValue, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if len(application.arguments) != 1:
            self.error(f"Argument count must be 1 for dictionary access", application.token)
            return NoneValue()

        if isinstance(identifier.petl_type, DictType):
            argument_value: PetlValue = self.evaluate(application.arguments[0], environment, identifier.petl_type.key_type)

            value: Optional[PetlValue] = next((v[1] for v in identifier.values if values_equal(v[0], argument_value)), None)
            if value and types_conform(application.token, value.petl_type, expected_type, self.error):
                return value
            else:
                self.error(f"Key does not exist in dictionary", application.arguments[0].token)
        return NoneValue()

    def evaluate_type_pattern(self, case: Case, match_value: PetlValue, environment: InterpreterEnvironment, expected_type: PetlType) -> Optional[PetlValue]:
        if isinstance(case.pattern, TypePattern):
            type_pattern: TypePattern = case.pattern
            token: Token = case.case_expression.token.file_position.to_string()
            if types_conform(token, match_value.petl_type, type_pattern.case_type, self.logger, no_error=True):
                case_environment: InterpreterEnvironment = copy(environment)
                case_environment.add(type_pattern.identifier, match_value)
                predicate_value: PetlValue = BoolValue(True)
                if type_pattern.predicate:
                    predicate_value: PetlValue = self.evaluate(type_pattern.predicate, case_environment, BoolType())
                if isinstance(predicate_value, BoolValue) and predicate_value.value:
                    return self.evaluate(case.case_expression, case_environment, expected_type)
        return None

    def evaluate_literal_pattern(self, case: Case, match_value: PetlValue, environment: InterpreterEnvironment, expected_type: PetlType) -> Optional[PetlValue]:
        if isinstance(case.pattern, LiteralPattern):
            literal_pattern: LiteralPattern = case.pattern
            token: Token = case.case_expression.token.file_position.to_string()
            if values_equal(match_value, self.literal_to_value(token, literal_pattern.literal)):
                return self.evaluate(case.case_expression, environment, expected_type)
        return None

    def evaluate_multiliteral_pattern(self, case: Case, match_value: PetlValue, environment: InterpreterEnvironment, expected_type: PetlType) -> Optional[PetlValue]:
        if isinstance(case.pattern, MultiLiteralPattern):
            multiliteral_pattern: MultiLiteralPattern = case.pattern
            token: Token = case.case_expression.token.file_position.to_string()
            if any(map(lambda l: values_equal(match_value, self.literal_to_value(token, l)), multiliteral_pattern.literals)):
                return self.evaluate(case.case_expression, environment, expected_type)
        return None

    def evaluate_range_pattern(self, case: Case, match_value: PetlValue, environment: InterpreterEnvironment, expected_type: PetlType) -> Optional[PetlValue]:
        if isinstance(case.pattern, RangePattern):
            range_pattern: RangePattern = case.pattern
            if isinstance(range_pattern.range, RangeDefinition):
                range_definition: PetlValue = self.evaluate_range_definition(range_pattern.range, ListType(IntType()))
                if isinstance(range_definition, ListValue):
                    list_values: List[PetlValue] = range_definition.values
                    if any(map(lambda v: values_equal(v, match_value), list_values)):
                        return self.evaluate(case.case_expression, environment, expected_type)
        return None

    def evaluate_match(self, match: Match, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        match_value: PetlValue = self.evaluate(match.match_expression, environment, AnyType())
        case_value: Optional[PetlValue] = None
        for case in match.cases:
            if isinstance(case.pattern, TypePattern):
                case_value = self.evaluate_type_pattern(case, match_value, environment, expected_type)
            elif isinstance(case.pattern, LiteralPattern):
                case_value = self.evaluate_literal_pattern(case, match_value, environment, expected_type)
            elif isinstance(case.pattern, MultiLiteralPattern):
                case_value = self.evaluate_multiliteral_pattern(case, match_value, environment, expected_type)
            elif isinstance(case.pattern, RangePattern):
                case_value = self.evaluate_range_pattern(case, match_value, environment, expected_type)
            elif isinstance(case.pattern, AnyPattern):
                case_value = self.evaluate(case.case_expression, environment, expected_type)
            else:
                self.error(f"Invalid pattern found", case.case_expression.token)
                return NoneValue()

            if case_value:
                return case_value

        if not case_value:
            self.error(f"Reached end of pattern-match, add catch-all case", match.token)
        return NoneValue()

    def evaluate_primitve(self, primitive: Primitive, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        pass

    def evaluate_reference(self, reference: Reference, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        reference_value: PetlValue = environment.get(reference.identifier, reference.token, self.error)
        if types_conform(reference.token, reference_value.petl_type, expected_type, self.error):
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
        def get_iterable_values(iterable: PetlValue) -> Optional[List[PetlValue]]:
            if isinstance(iterable, ListValue):
                return iterable.values
            elif isinstance(iterable, TupleValue):
                return iterable.values
            elif isinstance(iterable, DictValue):
                return list(map(lambda v: v[0], iterable.values))
            elif isinstance(iterable, TableValue):
                return iterable.rows

        iterable: PetlValue = self.evaluate(for_expression.iterable, environment, UnknownType())
        iterable_values: Optional[List[PetlValue]] = get_iterable_values(iterable)

        for iterable_value in iterable_values:
            for_body_environment: InterpreterEnvironment = copy(environment)
            for_body_environment.add(for_expression.reference, iterable_value)
            self.evaluate(for_expression.body, for_body_environment, AnyType())

        if for_expression.after_for_expression:
            return self.evaluate(for_expression.after_for_expression, environment, expected_type)
        else:
            return NoneValue()

    def evaluate_list_definition(self, list_definition: ListDefinition, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if isinstance(list_definition.petl_type, ListType):
            element_type: PetlType = list_definition.petl_type.list_type
            list_values: List[PetlValue] = list(map(lambda v: self.evaluate(v, environment, element_type), list_definition.values))
            if list_values and all(map(lambda v: types_conform(list_definition.token, v.petl_type,
                                                               list_values[0].petl_type, self.error), list_values)):
                element_type = list_values[0].petl_type
            else:
                element_type = UnknownType()
            list_type: PetlType = types_conform(list_definition.token, ListType(element_type), expected_type,
                                                self.logger)
            if list_type:
                return ListValue(list_type, list_values)
        return NoneValue()

    def evaluate_range_definition(self, range_definition: RangeDefinition, expected_type: PetlType) -> PetlValue:
        if isinstance(range_definition.start, IntLiteral) and isinstance(range_definition.end, IntLiteral):
            start_value: int = range_definition.start.value
            end_value: int = range_definition.end.value
            if start_value < 0 or end_value < 0:
                self.error(f"Range bounds cannot be negative", range_definition.token)
            elif types_conform(range_definition.token, ListType(IntType()), expected_type, self.error):
                return ListValue(ListType(IntType()), list(map(lambda l: IntValue(l), range(start_value, end_value + 1))))
        return NoneValue()

    def evaluate_tuple_definition(self, tuple_definition: TupleDefinition, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        if isinstance(tuple_definition.petl_type, TupleType):
            tuple_element_types: List[PetlType] = tuple_definition.petl_type.tuple_types
            tuple_values: List[PetlValue] = list(map(lambda tv, tet: self.evaluate(tv, environment, tet), tuple_definition.values, tuple_element_types))
            tuple_type: Optional[PetlType] = types_conform(tuple_definition.token,
                                                           TupleType(list(map(lambda tt: tt.petl_type, tuple_values))),
                                                           expected_type, self.error)
            if tuple_type:
                return TupleValue(tuple_definition.petl_type, tuple_values)
        return NoneValue()

    def evaluate_dict_definition(self, dict_definition: DictDefinition, environment: InterpreterEnvironment, expected_type: PetlType) -> PetlValue:
        def all_types_align(dict_values: List[Tuple[PetlValue, PetlValue]]) -> bool:
            return dict_values and \
                   all(map(lambda v: types_conform(dict_definition.token, v[0].petl_type, dict_values[0][0].petl_type,
                                                   self.logger), dict_values)) and \
                   all(map(lambda v: types_conform(dict_definition.token, v[1].petl_type, dict_values[0][1].petl_type,
                                                   self.logger), dict_values))

        if isinstance(dict_definition.petl_type, DictType):
            key_type: PetlType = dict_definition.petl_type.key_type
            entry_key_values: List[PetlValue] = list(map(lambda entry: self.evaluate(entry[0], environment, key_type), dict_definition.mapping))
            value_type: PetlType = dict_definition.petl_type.value_type
            entry_values: List[PetlValue] = list(map(lambda entry: self.evaluate(entry[1], environment, value_type), dict_definition.mapping))
            dict_values: List[Tuple[PetlValue, PetlValue]] = list(map(lambda k, v: (k, v), entry_key_values, entry_values))
            if all_types_align(dict_values):
                key_type = dict_values[0][0].petl_type
                value_type = dict_values[0][1].petl_type
            else:
                key_type = UnknownType()
                value_type = UnknownType()
            dict_type: PetlType = types_conform(dict_definition.token, DictType(key_type, value_type), expected_type,
                                                self.logger)
            if dict_type:
                return DictValue(dict_type, dict_values)
        return NoneValue()

    def evaluate_schema_definition(self, schema_definition: SchemaDefinition, expected_type: PetlType) -> PetlValue:
        if types_conform(schema_definition.token, schema_definition.petl_type, expected_type, self.error):
            columns: List[Tuple[StringValue, PetlType]] = list(map(lambda column: (StringValue(column[0]), column[1]), schema_definition.mapping))
            column_types: List[PetlType] = list(map(lambda column: column[1], columns))
            return SchemaValue(SchemaType(column_types), columns)
        return NoneValue()
