from petllang.utils.petl_enum import PetlBaseEnum


class Operator:
    class OperatorType(str, PetlBaseEnum):
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
        COLLECTION_CONCAT = "++",
        UNKNOWN = "???"

    def __init__(self, operator_type=OperatorType.UNKNOWN):
        self.operator_type = operator_type

    def to_string(self) -> str:
        return self.operator_type.value

    def is_arithmetic(self) -> bool:
        return self.operator_type == Operator.OperatorType.PLUS or \
               self.operator_type == Operator.OperatorType.MINUS or \
               self.operator_type == Operator.OperatorType.MULTIPLY or \
               self.operator_type == Operator.OperatorType.DIVIDE or \
               self.operator_type == Operator.OperatorType.MODULUS

    def is_boolean(self) -> bool:
        return self.operator_type == Operator.OperatorType.GREATER_THAN or \
               self.operator_type == Operator.OperatorType.LESS_THAN or \
               self.operator_type == Operator.OperatorType.GREATER_THAN_EQUAL_TO or \
               self.operator_type == Operator.OperatorType.LESS_THAN_EQUAL_TO or \
               self.operator_type == Operator.OperatorType.EQUAL or \
               self.operator_type == Operator.OperatorType.NOT_EQUAL or \
               self.operator_type == Operator.OperatorType.AND or \
               self.operator_type == Operator.OperatorType.OR

    def is_collection(self) -> bool:
        return self.operator_type == Operator.OperatorType.COLLECTION_CONCAT

    def get_precedence(self) -> int:
        if self.operator_type == Operator.OperatorType.AND or \
                self.operator_type == Operator.OperatorType.OR:
            return 0
        elif self.operator_type == Operator.OperatorType.PLUS or \
                self.operator_type == Operator.OperatorType.MINUS or \
                self.operator_type == Operator.OperatorType.COLLECTION_CONCAT:
            return 2
        elif self.operator_type == Operator.OperatorType.MULTIPLY or \
                self.operator_type == Operator.OperatorType.DIVIDE or \
                self.operator_type == Operator.OperatorType.MODULUS:
            return 3
        else:
            return 1

    def is_binary(self, min: int) -> bool:
        return (self.is_arithmetic() or self.is_boolean() or self.is_collection()) and (self.get_precedence() >= min)
