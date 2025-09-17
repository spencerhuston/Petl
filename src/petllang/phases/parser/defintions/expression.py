from abc import ABC
from dataclasses import dataclass, field
from pprint import pformat
from typing import Union, List, Optional, Tuple

from petllang.phases.interpreter.definitions.types import PetlType, UnknownType
from petllang.phases.lexer.definitions.token_petl import Token
from petllang.phases.parser.defintions.operator import Operator


@dataclass
class Expression(ABC):
    petl_type: PetlType = UnknownType()
    token: Token = Token()

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
    value: Union[int, bool, str, None] = None


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
    identifier: str = ""
    case_type: PetlType = UnknownType()
    predicate: Optional[Expression] = None


@dataclass
class LiteralPattern(Pattern):
    literal: Literal = NoneLiteral()


@dataclass
class MultiLiteralPattern(Pattern):
    literals: List[Literal] = field(default_factory=list)


@dataclass
class RangePattern(Pattern):
    range: Expression = UnknownExpression()


@dataclass
class AnyPattern(Pattern):
    pass


@dataclass
class UnknownPattern(Pattern):
    pass


@dataclass
class Case:
    pattern: Pattern = UnknownPattern()
    case_expression: Expression = UnknownExpression()


# End pattern matching definitions

#############################
# END AUXILIARY DEFINITIONS #
#############################

@dataclass
class LitExpression(Expression):
    literal: Literal = Literal()


@dataclass
class Let(Expression):
    identifiers: List[str] = field(default_factory=list)
    let_type: PetlType = UnknownType()
    let_expression: Expression = UnknownExpression()
    after_let_expression: Expression = UnknownExpression()


@dataclass
class Alias(Expression):
    identifier: str = ""
    alias_type: PetlType = UnknownType()
    after_alias_expression: Expression = UnknownExpression()


@dataclass
class Parameter:
    identifier: str = ""
    parameter_type: PetlType = UnknownType()
    token: Token = Token()


@dataclass
class Lambda(Expression):
    parameters: List[Parameter] = field(default_factory=list)
    return_type: PetlType = UnknownType()
    body: Expression = UnknownExpression()


@dataclass
class Application(Expression):
    identifier: Expression = UnknownExpression()
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class Match(Expression):
    match_expression: Expression = UnknownExpression()
    cases: List[Case] = field(default_factory=list)


@dataclass
class Primitive(Expression):
    operator: Operator = Operator()
    left: Expression = UnknownExpression()
    right: Expression = UnknownExpression()


@dataclass
class Reference(Expression):
    identifier: str = ""


@dataclass
class Branch(Expression):
    predicate: Expression = UnknownExpression()
    if_branch: Expression = UnknownExpression()
    else_branch: Expression = UnknownExpression()


@dataclass
class For(Expression):
    reference: str = ""
    iterable: Expression = UnknownExpression()
    body: Expression = UnknownExpression()
    after_for_expression: Expression = UnknownExpression()


@dataclass
class ListDefinition(Expression):
    values: List[Expression] = field(default_factory=list)


@dataclass
class RangeDefinition(Expression):
    start: Literal = Literal()
    end: Literal = Literal()


@dataclass
class TupleDefinition(Expression):
    values: List[Expression] = field(default_factory=list)


@dataclass
class DictDefinition(Expression):
    mapping: List[Tuple[Expression, Expression]] = field(default_factory=list)


@dataclass
class SchemaDefinition(Expression):
    mapping: List[Tuple[str, PetlType]] = field(default_factory=list)
