from typing import Optional

from petllang.query.interpreter.environment import QueryEnvironment
from petllang.query.interpreter.type_resolver import types_conform
from petllang.query.interpreter.types import QueryType, QueryBoolType, QueryUnknownType
from petllang.query.interpreter.value import values_equal, QueryValue, QueryIntValue, QueryStringValue, QueryCharValue, \
    QueryBoolValue, QueryRangeValue
from petllang.query.parser.expression import QueryIntLiteral, QueryLiteral, QueryExpression, QueryStringLiteral, \
    QueryCharLiteral, QueryBoolLiteral, QueryLitExpression, QueryPrimitive, QueryReference, QueryRangeDefinition
from petllang.query.parser.operator import QueryOperator


class QueryInterpreter:
    def literal_to_value(self, literal: QueryLiteral) -> QueryValue:
        if isinstance(literal, QueryIntLiteral):
            return QueryIntValue(literal.value)
        elif isinstance(literal, QueryBoolLiteral):
            return QueryBoolValue(literal.value)
        if isinstance(literal, QueryCharLiteral):
            return QueryCharValue(literal.value)
        elif isinstance(literal, QueryStringLiteral):
            return QueryStringValue(literal.value)
        else:
            raise Exception(f"Invalid type for pattern matching on literal value")

    def interpret(self, root: QueryExpression, environment: QueryEnvironment, token, error) -> QueryValue:
        try:
            return self.evaluate(root, environment, QueryBoolType())
        except Exception as interpreter_exception:
            error(f"Unhandled exception while interpreting: {interpreter_exception}", token)
            return QueryBoolValue(False)

    def evaluate(self, expression: QueryExpression, environment: QueryEnvironment, expected_type: QueryType) -> QueryValue:
        if isinstance(expression, QueryLitExpression):
            evaluated_value = self.evaluate_literal(expression, expected_type)
        elif isinstance(expression, QueryPrimitive):
            evaluated_value = self.evaluate_primitve(expression, environment, expected_type)
        elif isinstance(expression, QueryReference):
            evaluated_value = self.evaluate_reference(expression, environment, expected_type)
        elif isinstance(expression, QueryRangeDefinition):
            evaluated_value = self.evaluate_range_definition(expression)
        else:
            raise Exception(f"Invalid expression found")
        return evaluated_value

    def evaluate_literal(self, literal_expression: QueryLitExpression, expected_type: QueryType) -> QueryValue:
        if types_conform(literal_expression.query_type, expected_type):
            if isinstance(literal_expression.literal, QueryIntLiteral):
                return QueryIntValue(int(literal_expression.literal.value))
            elif isinstance(literal_expression.literal, QueryBoolLiteral):
                return QueryBoolValue(literal_expression.literal.value)
            elif isinstance(literal_expression.literal, QueryCharLiteral):
                return QueryCharValue(literal_expression.literal.value)
            elif isinstance(literal_expression.literal, QueryStringLiteral):
                return QueryStringValue(literal_expression.literal.value)
        raise Exception(f"Invalid expression found")

    def evaluate_arithmetic_operator(self, left: QueryValue, right: QueryValue, operator: QueryOperator) -> Optional[QueryValue]:
        if operator.operator_type == QueryOperator.QueryOperatorType.PLUS:
            if isinstance(left, QueryIntValue) and isinstance(right, QueryIntValue):
                return QueryIntValue(left.value + right.value)
            elif isinstance(left, QueryCharValue) and isinstance(right, QueryCharValue):
                return QueryStringValue(left.value + right.value)
            elif isinstance(left, QueryStringValue) and isinstance(right, QueryStringValue):
                return QueryStringValue(left.value + right.value)
            elif isinstance(left, QueryCharValue) and isinstance(right, QueryStringValue):
                return QueryStringValue(left.value + right.value)
            elif isinstance(left, QueryStringValue) and isinstance(right, QueryCharValue):
                return QueryStringValue(left.value + right.value)
        elif operator.operator_type == QueryOperator.QueryOperatorType.MINUS:
            if isinstance(left, QueryIntValue) and isinstance(right, QueryIntValue):
                return QueryIntValue(left.value - right.value)
        elif operator.operator_type == QueryOperator.QueryOperatorType.MULTIPLY:
            if isinstance(left, QueryIntValue) and isinstance(right, QueryIntValue):
                return QueryIntValue(left.value * right.value)
        elif operator.operator_type == QueryOperator.QueryOperatorType.DIVIDE:
            if isinstance(left, QueryIntValue) and isinstance(right, QueryIntValue):
                return QueryIntValue(int(left.value / right.value))
        elif operator.operator_type == QueryOperator.QueryOperatorType.MODULUS:
            if isinstance(left, QueryIntValue) and isinstance(right, QueryIntValue):
                return QueryIntValue(left.value % right.value)
        return None

    def evaluate_boolean_operator(self, left: QueryValue, right: QueryValue, operator: QueryOperator) -> Optional[QueryValue]:
        if operator.operator_type == QueryOperator.QueryOperatorType.GREATER_THAN:
            if isinstance(left, QueryIntValue) and isinstance(right, QueryIntValue):
                return QueryBoolValue(left.value > right.value)
        elif operator.operator_type == QueryOperator.QueryOperatorType.LESS_THAN:
            if isinstance(left, QueryIntValue) and isinstance(right, QueryIntValue):
                return QueryBoolValue(left.value < right.value)
        elif operator.operator_type == QueryOperator.QueryOperatorType.GREATER_THAN_EQUAL_TO:
            if isinstance(left, QueryIntValue) and isinstance(right, QueryIntValue):
                return QueryBoolValue(left.value >= right.value)
        elif operator.operator_type == QueryOperator.QueryOperatorType.LESS_THAN_EQUAL_TO:
            if isinstance(left, QueryIntValue) and isinstance(right, QueryIntValue):
                return QueryBoolValue(left.value <= right.value)
        elif operator.operator_type == QueryOperator.QueryOperatorType.EQUAL:
            return QueryBoolValue(values_equal(left, right))
        elif operator.operator_type == QueryOperator.QueryOperatorType.NOT_EQUAL:
            return QueryBoolValue(not values_equal(left, right))
        elif operator.operator_type == QueryOperator.QueryOperatorType.AND:
            if isinstance(left, QueryBoolValue) and isinstance(right, QueryBoolValue):
                return QueryBoolValue(left.value and right.value)
        elif operator.operator_type == QueryOperator.QueryOperatorType.OR:
            if isinstance(left, QueryBoolValue) and isinstance(right, QueryBoolValue):
                return QueryBoolValue(left.value or right.value)
        return None

    def evaluate_operator(self, left: QueryValue, right: QueryValue, operator: QueryOperator) -> QueryValue:
        if operator.is_arithmetic():
            return self.evaluate_arithmetic_operator(left, right, operator)
        elif operator.is_boolean():
            return self.evaluate_boolean_operator(left, right, operator)
        elif operator.is_contains() and isinstance(left, QueryIntValue) and isinstance(right, QueryRangeValue):
            return QueryBoolValue(right.start_value <= left.value <= right.end_value)
        else:
            raise Exception(f"Invalid types for operator \'{operator.to_string()}\'")

    def evaluate_primitve(self, primitive: QueryPrimitive, environment: QueryEnvironment, expected_type: QueryType) -> QueryValue:
        left_value: QueryValue = self.evaluate(primitive.left, environment, QueryUnknownType())
        right_value: QueryValue = self.evaluate(primitive.right, environment, QueryUnknownType())
        result_value: QueryValue = self.evaluate_operator(left_value, right_value, primitive.operator)
        if types_conform(result_value.query_type, expected_type):
            return result_value

    def evaluate_reference(self, reference: QueryReference, environment: QueryEnvironment, expected_type: QueryType) -> QueryValue:
        reference_value: QueryValue = environment.get(reference.identifier)
        if types_conform(reference_value.query_type, expected_type):
            return reference_value

    def evaluate_range_definition(self, range_definition: QueryRangeDefinition) -> QueryValue:
        if isinstance(range_definition.start, QueryIntLiteral) and isinstance(range_definition.end, QueryIntLiteral):
            start_value: int = range_definition.start.value
            end_value: int = range_definition.end.value
            if start_value < 0 or end_value < 0:
                raise Exception(f"Range bounds cannot be negative")
            return QueryRangeValue(start_value, end_value)
