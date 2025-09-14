from src.utils.petl_enum import BaseEnum


class QueryOperator:
    class QueryOperatorType(str, BaseEnum):
        PLUS = "+",
        MINUS = "-",
        MULTIPLY = "*",
        DIVIDE = "/",
        MODULUS = "%",
        GREATER_THAN = ">",
        LESS_THAN = "<",
        GREATER_THAN_EQUAL_TO = ">=",
        LESS_THAN_EQUAL_TO = "<=",
        EQUAL = "==",
        NOT_EQUAL = "!=",
        NOT = "not",
        AND = "and",
        OR = "or",
        IN = "in",
        UNKNOWN = "???"

    def __init__(self, operator_type=QueryOperatorType.UNKNOWN):
        self.operator_type = operator_type

    def to_string(self) -> str:
        return self.operator_type.value

    def is_arithmetic(self) -> bool:
        return self.operator_type == QueryOperator.QueryOperatorType.PLUS or \
               self.operator_type == QueryOperator.QueryOperatorType.MINUS or \
               self.operator_type == QueryOperator.QueryOperatorType.MULTIPLY or \
               self.operator_type == QueryOperator.QueryOperatorType.DIVIDE or \
               self.operator_type == QueryOperator.QueryOperatorType.MODULUS

    def is_boolean(self) -> bool:
        return self.operator_type == QueryOperator.QueryOperatorType.GREATER_THAN or \
               self.operator_type == QueryOperator.QueryOperatorType.LESS_THAN or \
               self.operator_type == QueryOperator.QueryOperatorType.GREATER_THAN_EQUAL_TO or \
               self.operator_type == QueryOperator.QueryOperatorType.LESS_THAN_EQUAL_TO or \
               self.operator_type == QueryOperator.QueryOperatorType.EQUAL or \
               self.operator_type == QueryOperator.QueryOperatorType.NOT_EQUAL or \
               self.operator_type == QueryOperator.QueryOperatorType.AND or \
               self.operator_type == QueryOperator.QueryOperatorType.OR

    def is_contains(self) -> bool:
        return self.operator_type == QueryOperator.QueryOperatorType.IN

    def get_precedence(self) -> int:
        if self.operator_type == QueryOperator.QueryOperatorType.AND or \
                self.operator_type == QueryOperator.QueryOperatorType.OR:
            return 0
        elif self.operator_type == QueryOperator.QueryOperatorType.PLUS or \
                self.operator_type == QueryOperator.QueryOperatorType.MINUS or \
                self.operator_type == QueryOperator.QueryOperatorType.IN:
            return 2
        elif self.operator_type == QueryOperator.QueryOperatorType.MULTIPLY or \
                self.operator_type == QueryOperator.QueryOperatorType.DIVIDE or \
                self.operator_type == QueryOperator.QueryOperatorType.MODULUS:
            return 3
        else:
            return 1

    def is_binary(self, min: int) -> bool:
        return (self.is_arithmetic() or self.is_boolean() or self.is_contains()) and (self.get_precedence() >= min)
