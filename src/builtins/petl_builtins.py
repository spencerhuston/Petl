from src.phases.environment import InterpreterEnvironment
from src.semantic_defintions.petl_expression import UnknownExpression, Application
from src.semantic_defintions.petl_value import *


class Builtin(ABC):
    name: str
    func_type: FuncType
    parameters: List[Tuple[str, PetlType]] = []

    @abstractmethod
    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        pass

    def to_value(self) -> FuncValue:
        body: Expression = UnknownExpression()
        environment = InterpreterEnvironment()
        return FuncValue(self.func_type, self, self.parameters, body, environment)


def get_builtin(name: str) -> Builtin:
    if name == "readln":
        return ReadLn()
    elif name == "print":
        return Print()
    elif name == "println":
        return PrintLn()
    elif name == "map":
        return Map()
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
        self.func_type = FuncType([], StringType())
        self.parameters = []

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        return StringValue(input())


class Print(Builtin):
    def __init__(self):
        self.name = "print"
        self.func_type = FuncType([AnyType()], NoneType())
        self.parameters = [("value", AnyType())]

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        value: PetlValue = environment.get("value", application.token, error)
        print(value.to_string().encode().decode('unicode_escape'), end="")
        return NoneValue()


class PrintLn(Builtin):
    def __init__(self):
        self.name = "println"
        self.func_type = FuncType([AnyType()], NoneType())
        self.parameters = [("value", AnyType())]

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        value: PetlValue = environment.get("value", application.token, error)
        print(value.to_string().encode().decode('unicode_escape'))
        return NoneValue()


class Map(Builtin):
    def __init__(self):
        self.name = "map"
        self.func_type = FuncType([IterableType(), FuncType([AnyType()], AnyType())], ListType(AnyType()))
        self.parameters = [
            ("iterable", IterableType()),
            ("mapping_function", FuncType([AnyType()], AnyType()))
        ]

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        pass


class Filter(Builtin):
    def __init__(self):
        self.name = "filter"
        self.func_type = FuncType([IterableType(), FuncType([AnyType()], BoolType())], ListType(AnyType()))
        self.parameters = [
            ("iterable", IterableType()),
            ("filter_function", FuncType([AnyType()], AnyType()))
        ]

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
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
        self.func_type = FuncType([StringType(), IntType(), IntType()], StringType())
        self.parameters = [
            ("string_value", StringType()),
            ("start", IntType()),
            ("end", IntType())
        ]

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        string_value: PetlValue = environment.get("string_value", application.token, error)
        start_value: PetlValue = environment.get("string_value", application.token, error)
        end_value: PetlValue = environment.get("string_value", application.token, error)

        if isinstance(string_value, StringValue) and isinstance(start_value, IntValue) and isinstance(end_value, IntValue):
            string: str = string_value.value
            start: int = start_value.value
            end: int = end_value.value

            if start < 0 or end < 0 or \
                    start >= len(string) or end >= len(string) or \
                    start_value > end_value:
                error(f"Invalid substr range value(s)", application.token)
                return NoneValue()

            return StringValue(string[start_value:end_value])
        return NoneValue()


class Len(Builtin):
    def __init__(self):
        self.name = "len"
        self.func_type = FuncType([IterableType()], IntType())
        self.parameters = [("iterable", IterableType())]

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        iterable: PetlValue = environment.get("iterable", application.token, error)
        if isinstance(iterable, ListValue):
            return IntValue(len(iterable.values))
        elif isinstance(iterable, TupleValue):
            return IntValue(len(iterable.values))
        elif isinstance(iterable, DictValue):
            return IntValue(len(iterable.values))
        elif isinstance(iterable, TableValue):
            return IntValue(len(iterable.rows))
        else:
            error(f"Length function requires iterable type, not {iterable.petl_type.to_string()}", application.token)
            return NoneValue()


class Type(Builtin):
    def __init__(self):
        self.name = "type"
        self.func_type = FuncType([AnyType()], StringType())
        self.parameters = [("value", AnyType())]

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        return StringValue(environment.get("value", application.token, error).petl_type.to_string())


class ToStr(Builtin):
    def __init__(self):
        self.name = "toStr"
        self.func_type = FuncType([IntType()], StringType())
        self.parameters = [("i", IntType())]

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        value: PetlValue = environment.get("i", application.token, error)
        if isinstance(value, IntValue):
            return StringValue(str(value.value))
        return NoneValue()


class ToInt(Builtin):
    def __init__(self):
        self.name = "toInt"
        self.func_type = FuncType([StringType()], IntType())
        self.parameters = [("s", StringType())]

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        value: PetlValue = environment.get("s", application.token, error)
        if isinstance(value, StringValue):
            return IntValue(int(value.value))
        return NoneValue()


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
