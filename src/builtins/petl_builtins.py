from src.phases.environment import InterpreterEnvironment
from src.semantic_defintions.petl_expression import UnknownExpression
from src.semantic_defintions.petl_value import *
from src.tokens.petl_token import Token
from src.utils.log import Log


class Builtin(ABC):
    name: str
    lambda_type: LambdaType

    @abstractmethod
    def evaluate(self, token: Token, argument_values: List[PetlValue], environment: InterpreterEnvironment, error) -> PetlValue:
        pass

    @abstractmethod
    def to_value(self) -> LambdaValue:
        pass

    def _to_value(self, parameters: List[Tuple[str, PetlType]]) -> LambdaValue:
        body: Expression = UnknownExpression()
        environment: InterpreterEnvironment = InterpreterEnvironment()
        return LambdaValue(self.lambda_type, self, parameters, body, environment)


def get_builtin(name: str) -> Builtin:
    if name == "readln":
        return ReadLn()
    elif name == "print":
        return Print()
    elif name == "println":
        return PrintLn()
    elif name == "substr":
        return Substr()
    elif name == "len":
        return Len()
    elif name == "type":
        return Type()
    elif name == "toStr":
        return ToStr()
    elif name == "toInt":
        return ToInt()


class ReadLn(Builtin):
    def __init__(self):
        self.name = "readln"
        self.lambda_type = LambdaType([], StringType())

    def evaluate(self, token: Token, argument_values: List[PetlValue], environment: InterpreterEnvironment, logger: Log) -> PetlValue:
        return StringValue(input())

    def to_value(self) -> LambdaValue:
        parameters = []
        return self._to_value(parameters)


class Print(Builtin):
    def __init__(self):
        self.name = "print"
        self.lambda_type = LambdaType([AnyType()], NoneType())

    def evaluate(self, token: Token, argument_values: List[PetlValue], environment: InterpreterEnvironment, error) -> PetlValue:
        print(argument_values[0].to_string().encode().decode('unicode_escape'), end="")
        return NoneValue()

    def to_value(self) -> LambdaValue:
        parameters = [("str", AnyType())]
        return self._to_value(parameters)


class PrintLn(Builtin):
    def __init__(self):
        self.name = "println"
        self.lambda_type = LambdaType([AnyType()], NoneType())

    def evaluate(self, token: Token, argument_values: List[PetlValue], environment: InterpreterEnvironment, error) -> PetlValue:
        print(argument_values[0].to_string().encode().decode('unicode_escape'))
        return NoneValue()

    def to_value(self) -> LambdaValue:
        parameters = [("str", AnyType())]
        return self._to_value(parameters)


class Map(Builtin):
    pass


class Filter(Builtin):
    pass


class Zip(Builtin):
    pass


class Foldl(Builtin):
    pass


class Foldr(Builtin):
    pass


class Slice(Builtin):
    pass


class Substr(Builtin):
    def __init__(self):
        self.name = "substr"
        self.lambda_type = LambdaType([StringType(), IntType(), IntType()], StringType())

    def evaluate(self, token: Token, argument_values: List[PetlValue], environment: InterpreterEnvironment, error) -> PetlValue:
        string_value: str = argument_values[0].value
        start_value: int = argument_values[1].value
        end_value: int = argument_values[2].value

        if start_value < 0 or end_value < 0 or \
                start_value >= len(string_value) or end_value >= len(string_value) or \
                start_value > end_value:
            error(f"Invalid substr range value(s)", token)
            return NoneValue()

        return StringValue(string_value.replace('\"', '')[start_value:end_value])

    def to_value(self) -> LambdaValue:
        parameters = [
            ("str", StringType()),
            ("start", IntType()),
            ("end", IntType())
        ]
        return self._to_value(parameters)


class Len(Builtin):
    def __init__(self):
        self.name = "len"
        self.lambda_type = LambdaType([AnyType()], IntType())

    def evaluate(self, token: Token, argument_values: List[PetlValue], environment: InterpreterEnvironment, error) -> PetlValue:
        argument: PetlValue = argument_values[0]
        if isinstance(argument, ListValue):
            return IntValue(len(argument.values))
        elif isinstance(argument, TupleValue):
            return IntValue(len(argument.values))
        elif isinstance(argument, DictValue):
            return IntValue(len(argument.values))
        elif isinstance(argument, SchemaValue):
            return IntValue(len(argument.values))
        elif isinstance(argument, TableValue):
            return IntValue(len(argument.rows))
        else:
            error(f"Length function requires iterable type, not {argument.petl_type.to_string()}", token)
            return NoneValue()

    def to_value(self) -> LambdaValue:
        parameters = [("collection", AnyType())]
        return self._to_value(parameters)


class Type(Builtin):
    def __init__(self):
        self.name = "type"
        self.lambda_type = LambdaType([AnyType()], StringType())

    def evaluate(self, token: Token, argument_values: List[PetlValue], environment: InterpreterEnvironment, error) -> PetlValue:
        return StringValue(argument_values[0].petl_type.to_string())

    def to_value(self) -> LambdaValue:
        parameters = [("type_value", AnyType())]
        return self._to_value(parameters)


class ToStr(Builtin):
    def __init__(self):
        self.name = "toStr"
        self.lambda_type = LambdaType([IntType()], StringType())

    def evaluate(self, token: Token, argument_values: List[PetlValue], environment: InterpreterEnvironment, error) -> PetlValue:
        return StringValue(str(argument_values[0].value))

    def to_value(self) -> LambdaValue:
        parameters = [("i", IntType())]
        return self._to_value(parameters)


class ToInt(Builtin):
    def __init__(self):
        self.name = "toInt"
        self.lambda_type = LambdaType([StringType()], IntType())

    def evaluate(self, token: Token, argument_values: List[PetlValue], environment: InterpreterEnvironment, error) -> PetlValue:
        return IntValue(int(argument_values[0].value.replace('\"', '')))

    def to_value(self) -> LambdaValue:
        parameters = [("s", StringType())]
        return self._to_value(parameters)


class CreateTable(Builtin):
    pass


class ReadCsv(Builtin):
    pass


class WriteToCsv(Builtin):
    pass


class Join(Builtin):
    pass


class With(Builtin):
    pass


class Where(Builtin):
    pass


class Select(Builtin):
    pass


class Drop(Builtin):
    pass


class Column(Builtin):
    pass


class Collect(Builtin):
    pass


class Count(Builtin):
    pass
