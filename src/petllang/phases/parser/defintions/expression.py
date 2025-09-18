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
    identifier: str = field(default="")
    case_type: PetlType = field(default=UnknownType())
    predicate: Optional[Expression] = field(default=None)


@dataclass
class LiteralPattern(Pattern):
    literal: Literal = field(default=NoneLiteral())


@dataclass
class MultiLiteralPattern(Pattern):
    literals: List[Literal] = field(default_factory=list)


@dataclass
class RangePattern(Pattern):
    range: Expression = field(default=UnknownExpression())


@dataclass
class AnyPattern(Pattern):
    pass


@dataclass
class UnknownPattern(Pattern):
    pass


@dataclass
class Case:
    pattern: Pattern = field(default=UnknownPattern())
    case_expression: Expression = field(default=UnknownExpression())


# End pattern matching definitions

#############################
# END AUXILIARY DEFINITIONS #
#############################

@dataclass
class LitExpression(Expression):
    literal: Literal = field(default=Literal())


@dataclass
class Let(Expression):
    identifiers: List[str] = field(default_factory=list)
    let_type: PetlType = field(default=UnknownType())
    let_expression: Expression = field(default=UnknownExpression())
    after_let_expression: Expression = field(default=UnknownExpression())


@dataclass
class Alias(Expression):
    identifier: str = ""
    alias_type: PetlType = field(default=UnknownType())
    after_alias_expression: Expression = field(default=UnknownExpression())


@dataclass
class Parameter:
    identifier: str = ""
    parameter_type: PetlType = field(default=UnknownType())
    token: Token = Token()


@dataclass
class Lambda(Expression):
    parameters: List[Parameter] = field(default_factory=list)
    return_type: PetlType = field(default=UnknownType())
    body: Expression = field(default=UnknownExpression())


@dataclass
class Application(Expression):
    identifier: Expression = field(default=UnknownExpression())
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class Match(Expression):
    match_expression: Expression = field(default=UnknownExpression())
    cases: List[Case] = field(default_factory=list)


@dataclass
class Primitive(Expression):
    operator: Operator = Operator()
    left: Expression = field(default=UnknownExpression())
    right: Expression = field(default=UnknownExpression())


@dataclass
class Reference(Expression):
    identifier: str = ""


@dataclass
class Branch(Expression):
    predicate: Expression = field(default=UnknownExpression())
    if_branch: Expression = field(default=UnknownExpression())
    else_branch: Expression = field(default=UnknownExpression())


@dataclass
class For(Expression):
    reference: str = ""
    iterable: Expression = field(default=UnknownExpression())
    body: Expression = field(default=UnknownExpression())
    after_for_expression: Expression = field(default=UnknownExpression())


@dataclass
class ListDefinition(Expression):
    values: List[Expression] = field(default_factory=list)


@dataclass
class RangeDefinition(Expression):
    start: Literal = field(default=Literal())
    end: Literal = field(default=Literal())


@dataclass
class TupleDefinition(Expression):
    values: List[Expression] = field(default_factory=list)


@dataclass
class DictDefinition(Expression):
    mapping: List[Tuple[Expression, Expression]] = field(default_factory=list)


@dataclass
class SchemaDefinition(Expression):
    mapping: List[Tuple[str, PetlType]] = field(default_factory=list)
