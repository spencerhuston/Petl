import dataclasses
import json
from abc import ABC
from dataclasses import dataclass, field
from typing import Union, List, Optional, Tuple

from src.semantic_defintions.operator import Operator
from src.semantic_defintions.petl_types import PetlType, UnknownType
from src.tokens.petl_token import Token


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclass
class Expression(ABC):
    petl_type: PetlType = UnknownType()
    token: Token = Token()

    def to_json_string(self):
        return json.dumps(self, cls=EnhancedJSONEncoder)


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
    identifier: str = ""
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
    after_lambda_expression: Expression = UnknownExpression()


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
    mapping: List[Tuple[Literal, Expression]] = field(default_factory=list)


@dataclass
class SchemaDefinition(Expression):
    mapping: List[Tuple[str, PetlType]] = field(default_factory=list)
