from abc import ABC
from dataclasses import dataclass
from typing import Union, List, Optional

from src.semantic_defintions.petl_types import PetlType, UnknownType
from src.tokens.petl_token import Token


@dataclass
class Expression(ABC):
    petl_type: PetlType = UnknownType()
    token: Token = Token()
    pass


class UnknownExpression(Expression):
    pass


###############################
# START AUXILIARY DEFINITIONS #
###############################

# Start literal definitions

class Literal(ABC):
    value: Union[int, bool, str, None] = None


class IntLiteral(Literal):
    pass


class BoolLiteral(Literal):
    pass


class CharLiteral(Literal):
    pass


class StringLiteral(Literal):
    pass


class NoneLiteral(Literal):
    pass


# End literal definitions

# Start pattern matching definitions
class Pattern(ABC):
    pass


class TypePattern(Pattern):
    identifier: str = ""
    case_type: PetlType = UnknownType()
    predicate: Optional[Expression] = None


class LiteralPattern(Pattern):
    literal: Literal = NoneLiteral()


class MultiLiteralPattern(Pattern):
    literals: List[Literal] = []


class RangePattern(Pattern):
    range: Expression = UnknownExpression()


class AnyPattern(Pattern):
    pass


class UnknownPattern(Pattern):
    pass


class Case:
    pattern: Pattern = UnknownPattern()
    case_expression: Expression = UnknownExpression()


# End pattern matching definitions

#############################
# END AUXILIARY DEFINITIONS #
#############################

class LitExpression(Expression):
    literal: Literal = Literal()


@dataclass
class Let(Expression):
    identifier: str = ""
    let_type: PetlType = UnknownType()
    let_expression: Expression = UnknownExpression()
    after_let_expression: Expression = UnknownExpression()


class Alias(Expression):
    identifier: str = ""
    alias_type: PetlType = UnknownType()
    after_alias_expression: Expression = UnknownExpression()


class Parameter:
    identifier: str = ""
    parameter_type: PetlType = UnknownType()
    token: Token = Token()


class Lambda(Expression):
    parameters: List[Parameter] = []
    return_type: PetlType = UnknownType()
    after_lambda_expression: Expression = UnknownExpression()


class Application(Expression):
    identifier: Expression = UnknownExpression()
    arguments: List[Expression] = []


class Match(Expression):
    match_expression: Expression = UnknownExpression()
    cases: List[Case] = []


# class Primitive(Expression):
#     operator: Operator = UnknownOperator()
#     left: Expression = UnknownExpression()
#     right: Expression = UnknownExpression()


class Reference(Expression):
    identifier: str = ""


class Branch(Expression):
    predicate: Expression = UnknownExpression()
    if_branch: Expression = UnknownExpression()
    else_branch: Expression = UnknownExpression()


class For(Expression):
    reference: str = ""
    iterable: Expression = UnknownExpression()
    body: Expression = UnknownExpression()


class ListDefinition(Expression):
    values: List[Expression] = []


class TupleDefinition(Expression):
    values: List[Expression] = []


class DictDefinition(Expression):
    mapping: dict[Literal, Expression] = {}


class SchemaDefinition(Expression):
    mapping: dict[str, PetlType] = {}
