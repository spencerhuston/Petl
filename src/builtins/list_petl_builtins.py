from copy import deepcopy

from src.builtins.petl_builtin_definitions import Builtin, extract_element_type
from src.phases.environment import InterpreterEnvironment
from src.phases.type_resolver import types_conform
from src.semantic_defintions.petl_expression import Application
from src.semantic_defintions.petl_value import *
from src.tokens.petl_keyword import Keyword


class Insert(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(AnyType())),
            ("value", AnyType()),
            ("index", IntType())
        ]
        Builtin.__init__(self, Keyword.INSERT.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        value: PetlValue = environment.get("value", application.token, error)
        index_value: PetlValue = environment.get("index", application.token, error)
        if isinstance(list_value, ListValue) and isinstance(index_value, IntValue):
            list_values: List[PetlValue] = deepcopy(list_value.values)
            index_value: IntValue = index_value
            list_values.insert(index_value.value, value)
            return ListValue(list_value.petl_type, list_values)
        return NoneValue()


class Remove(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(AnyType())),
            ("index", IntType())
        ]
        Builtin.__init__(self, Keyword.REMOVE.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        index_value: PetlValue = environment.get("index", application.token, error)
        if isinstance(list_value, ListValue) and isinstance(index_value, IntValue):
            list_values: List[PetlValue] = deepcopy(list_value.values)
            list_values.pop(index_value.value)
            return ListValue(list_value.petl_type, list_values)
        return NoneValue()


class Replace(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(AnyType())),
            ("index", IntType()),
            ("new_value", AnyType())
        ]
        Builtin.__init__(self, Keyword.REPLACE.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        index_value: PetlValue = environment.get("index", application.token, error)
        new_value: PetlValue = environment.get("new_value", application.token, error)
        if isinstance(list_value, ListValue) and isinstance(index_value, IntValue):
            list_values: List[PetlValue] = deepcopy(list_value.values)
            list_values[index_value.value] = new_value
            return ListValue(list_value.petl_type, list_values)
        return NoneValue()
    pass


class Front(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(AnyType()))
        ]
        Builtin.__init__(self, Keyword.FRONT.value, parameters, AnyType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        if isinstance(list_value, ListValue) and list_value.values:
            return list_value.values[0]
        return NoneValue()


class Back(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(AnyType()))
        ]
        Builtin.__init__(self, Keyword.BACK.value, parameters, AnyType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        if isinstance(list_value, ListValue) and list_value.values:
            return list_value.values[-1]
        return NoneValue()


class Head(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(AnyType()))
        ]
        Builtin.__init__(self, Keyword.HEAD.value, parameters, AnyType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        if isinstance(list_value, ListValue) and list_value.values:
            return ListValue(list_value.petl_type, deepcopy(list_value.values)[1:])
        return NoneValue()


class Tail(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(AnyType()))
        ]
        Builtin.__init__(self, Keyword.TAIL.value, parameters, AnyType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        if isinstance(list_value, ListValue) and list_value.values:
            return ListValue(list_value.petl_type, deepcopy(list_value.values)[:-1])
        return NoneValue()


class Slice(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(AnyType())),
            ("start", IntType()),
            ("end", IntType())
        ]
        Builtin.__init__(self, Keyword.SLICE.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        start_value: PetlValue = environment.get("string_value", application.token, error)
        end_value: PetlValue = environment.get("string_value", application.token, error)
        element_type: PetlType = extract_element_type(list_value)

        if isinstance(list_value, ListValue) and isinstance(start_value, IntValue) and isinstance(end_value, IntValue):
            list_values: List[PetlValue] = list_value.values
            start: int = start_value.value
            end: int = end_value.value

            if start < 0 or end < 0 or \
                    start >= len(list_values) or end >= len(list_values) or \
                    start_value > end_value:
                error(f"Invalid slice range value(s)", application.token)
                return NoneValue()

            return ListValue(element_type, list_values)
        return NoneValue()


class Contains(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(AnyType())),
            ("value", AnyType())
        ]
        Builtin.__init__(self, Keyword.CONTAINS.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        value: PetlValue = environment.get("value", application.token, error)
        if isinstance(list_value, ListValue):
            list_values: List[PetlValue] = list_value.values
            contains: bool = any(map(lambda v: values_equal(v, value), list_values))
            return BoolValue(contains)
        return BoolValue(False)


class Find(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(AnyType())),
            ("value", AnyType())
        ]
        Builtin.__init__(self, Keyword.FIND.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        value: PetlValue = environment.get("value", application.token, error)
        if isinstance(list_value, ListValue):
            for i, v in enumerate(list_value.values):
                if values_equal(v, value):
                    return IntValue(i)
        return IntValue(-1)


class Fill(Builtin):
    def __init__(self):
        parameters = [
            ("count", IntType()),
            ("value", AnyType())
        ]
        Builtin.__init__(self, Keyword.FILL.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        count_value: PetlValue = environment.get("count", application.token, error)
        value: PetlValue = environment.get("value", application.token, error)
        if isinstance(count_value, IntValue):
            if count_value.value <= 0:
                error(f"Fill requires positive non-zero integer value for \'count\'", application.token)
            else:
                list_values: List[PetlValue] = [value] * count_value.value
                return ListValue(ListType(value.petl_type), list_values)
        return NoneValue()


class Reverse(Builtin):
    def __init__(self):
        parameters = [
            ("list", ListType(AnyType()))
        ]
        Builtin.__init__(self, Keyword.REVERSE.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list_value: PetlValue = environment.get("list", application.token, error)
        if isinstance(list_value, ListValue):
            list_values: List[PetlValue] = deepcopy(list_value.values)
            list_values.reverse()
            return ListValue(list_value.petl_type, list_values)
        return NoneValue()


class Set(Builtin):
    def __init__(self):
        parameters = [
            ("list1", ListType(AnyType())),
            ("list2", ListType(AnyType()))
        ]
        Builtin.__init__(self, Keyword.SET.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list1_value: PetlValue = environment.get("list1", application.token, error)
        list2_value: PetlValue = environment.get("list2", application.token, error)
        if types_conform(application.token, list1_value.petl_type, list2_value.petl_type, error):
            if isinstance(list1_value, ListValue) and isinstance(list2_value, ListValue):
                all_values: List[PetlValue] = deepcopy(list1_value.values)
                all_values.extend(list2_value.values)
                set_values: List[PetlValue] = []

                def add_unique_value(value: PetlValue):
                    for v in set_values:
                        if values_equal(value, v):
                            return
                    set_values.append(value)

                for v in all_values:
                    add_unique_value(v)
                return ListValue(list1_value.petl_type, set_values)
        return NoneValue()


class Intersect(Builtin):
    def __init__(self):
        parameters = [
            ("list1", ListType(AnyType())),
            ("list2", ListType(AnyType()))
        ]
        Builtin.__init__(self, Keyword.INTERSECT.value, parameters, ListType(AnyType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        list1_value: PetlValue = environment.get("list1", application.token, error)
        list2_value: PetlValue = environment.get("list2", application.token, error)
        if types_conform(application.token, list1_value.petl_type, list2_value.petl_type, error):
            if isinstance(list1_value, ListValue) and isinstance(list2_value, ListValue):
                list1_values: List[PetlValue] = deepcopy(list1_value.values)
                list2_values: List[PetlValue] = deepcopy(list2_value.values)
                intersect_values: List[PetlValue] = []

                def add_unique_value(value: PetlValue):
                    for v in intersect_values:
                        if values_equal(value, v):
                            return
                    intersect_values.append(value)

                for v1 in list1_values:
                    for v2 in list2_values:
                        if values_equal(v1, v2):
                            add_unique_value(v1)
                return ListValue(list1_value.petl_type, intersect_values)
        return NoneValue()
