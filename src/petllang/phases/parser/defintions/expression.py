from abc import ABC
from dataclasses import dataclass, field
from pprint import pformat
from typing import Union, List, Optional, Tuple

from petllang.phases.interpreter.definitions.types import PetlType, UnknownType
from petllang.phases.lexer.definitions.token_petl import Token
from petllang.phases.parser.defintions.operator import Operator


@dataclass
class Expression(ABC):
    petl_type: PetlType = field(default_factory=UnknownType)
    token: Token = field(default_factory=Token)

    def to_string(self):
        return pformat(self)


@dataclass
class UnknownExpression(Expression):
    pass


###############################
# START AUXILIARY DEFINITIONS #
###############################

# Start literal definitions

@dataclass
class Literal(ABC):
    value: Union[int, bool, str, None] = field(default_factory=str)


@dataclass
class IntLiteral(Literal):
    pass


@dataclass
class BoolLiteral(Literal):
    pass


@dataclass
class CharLiteral(Literal):
    pass


@dataclass
class StringLiteral(Literal):
    pass


@dataclass
class NoneLiteral(Literal):
    pass


# End literal definitions

# Start pattern matching definitions
@dataclass
class Pattern(ABC):
    pass


@dataclass
class TypePattern(Pattern):
    identifier: str = field(default_factory=str)
    case_type: PetlType = field(default_factory=UnknownType)
    predicate: Optional[Expression] = field(default_factory=UnknownExpression)


@dataclass
class LiteralPattern(Pattern):
    literal: Literal = field(default_factory=NoneLiteral)


@dataclass
class MultiLiteralPattern(Pattern):
    literals: List[Literal] = field(default_factory=list)


@dataclass
class RangePattern(Pattern):
    range: Expression = field(default_factory=UnknownExpression)


@dataclass
class AnyPattern(Pattern):
    pass


@dataclass
class UnknownPattern(Pattern):
    pass


@dataclass
class Case:
    pattern: Pattern = field(default_factory=UnknownPattern)
    case_expression: Expression = field(default_factory=UnknownExpression)


# End pattern matching definitions

#############################
# END AUXILIARY DEFINITIONS #
#############################

@dataclass
class LitExpression(Expression):
    literal: Literal = field(default_factory=Literal)


@dataclass
class Let(Expression):
    identifiers: List[str] = field(default_factory=list)
    let_type: PetlType = field(default_factory=UnknownType)
    let_expression: Expression = field(default_factory=UnknownExpression)
    after_let_expression: Expression = field(default_factory=UnknownExpression)


@dataclass
class Alias(Expression):
    identifier: str = field(default_factory=str)
    alias_type: PetlType = field(default_factory=UnknownType)
    after_alias_expression: Expression = field(default_factory=UnknownExpression)


@dataclass
class Parameter:
    identifier: str = field(default_factory=str)
    parameter_type: PetlType = field(default_factory=UnknownType)
    token: Token = field(default_factory=Token)


@dataclass
class Lambda(Expression):
    parameters: List[Parameter] = field(default_factory=list)
    return_type: PetlType = field(default_factory=UnknownType)
    body: Expression = field(default_factory=UnknownExpression)


@dataclass
class Application(Expression):
    identifier: Expression = field(default_factory=UnknownExpression)
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class Match(Expression):
    match_expression: Expression = field(default_factory=UnknownExpression)
    cases: List[Case] = field(default_factory=list)


@dataclass
class Primitive(Expression):
    operator: Operator = field(default_factory=Operator)
    left: Expression = field(default_factory=UnknownExpression)
    right: Expression = field(default_factory=UnknownExpression)


@dataclass
class Reference(Expression):
    identifier: str = field(default_factory=str)


@dataclass
class Branch(Expression):
    predicate: Expression = field(default_factory=UnknownExpression)
    if_branch: Expression = field(default_factory=UnknownExpression)
    else_branch: Expression = field(default_factory=UnknownExpression)


@dataclass
class For(Expression):
    reference: str = field(default_factory=str)
    iterable: Expression = field(default_factory=UnknownExpression)
    body: Expression = field(default_factory=UnknownExpression)
    after_for_expression: Expression = field(default_factory=UnknownExpression)


@dataclass
class ListDefinition(Expression):
    values: List[Expression] = field(default_factory=list)


@dataclass
class RangeDefinition(Expression):
    start: Literal = field(default_factory=Literal)
    end: Literal = field(default_factory=Literal)


@dataclass
class TupleDefinition(Expression):
    values: List[Expression] = field(default_factory=list)


@dataclass
class DictDefinition(Expression):
    mapping: List[Tuple[Expression, Expression]] = field(default_factory=list)


@dataclass
class SchemaDefinition(Expression):
    mapping: List[Tuple[str, PetlType]] = field(default_factory=list)
