import src.builtins.io_petl_builtins
from src.semantic_defintions.petl_expression import IntLiteral, LitExpression
from src.semantic_defintions.petl_types import IntType, BoolType, StringType, ListType, TupleType, DictType, \
    SchemaType, TableType, FuncType
from src.semantic_defintions.petl_value import values_equal, IntValue, BoolValue, CharValue, StringValue, NoneValue, \
    ListValue, TupleValue, DictValue, SchemaValue, TableValue, FuncValue


def test_values_equal():
    assert values_equal(IntValue(5), IntValue(5))
    assert values_equal(BoolValue(True), BoolValue(True))
    assert values_equal(CharValue("a"), CharValue("a"))
    assert values_equal(StringValue("test"), StringValue("test"))
    assert values_equal(NoneValue(), NoneValue())


def test_values_equal_invalid():
    assert not values_equal(IntValue(5), IntValue(4))
    assert not values_equal(BoolValue(True), BoolValue(False))
    assert not values_equal(CharValue("a"), CharValue("b"))
    assert not values_equal(StringValue("test"), StringValue("test2"))


def test_values_equal_collection():
    list_value = ListValue(ListType(IntType()), [IntValue(5)])
    assert values_equal(list_value, list_value)
    tuple_value = TupleValue(TupleType([IntType(), BoolType()]), [IntValue(5), BoolValue(True)])
    assert values_equal(tuple_value, tuple_value)
    dict_value = DictValue(DictType(key_type=IntType(), value_type=BoolType()), [(IntValue(5), BoolValue(True))])
    assert values_equal(dict_value, dict_value)


def test_values_equal_collection_invalid():
    list_value1 = ListValue(ListType(IntType()), [IntValue(5)])
    list_value2 = ListValue(ListType(IntType()), [IntValue(4)])
    assert not values_equal(list_value1, list_value2)
    tuple_value1 = TupleValue(TupleType([IntType(), BoolType()]), [IntValue(5), BoolValue(True)])
    tuple_value2 = TupleValue(TupleType([IntType(), BoolType()]), [IntValue(4), BoolValue(False)])
    assert not values_equal(tuple_value1, tuple_value2)
    dict_value1 = DictValue(DictType(key_type=IntType(), value_type=BoolType()), [(IntValue(5), BoolValue(True))])
    dict_value2 = DictValue(DictType(key_type=IntType(), value_type=BoolType()), [(IntValue(4), BoolValue(False))])
    assert not values_equal(dict_value1, dict_value2)


def test_values_equal_nested_collection():
    tt = TupleType()
    lt = ListType(IntType())
    dt = DictType(IntType(), BoolType())
    tt.tuple_types = [lt, dt]
    tuple_value = TupleValue(tt, [ListValue(lt, [IntValue(5)]), DictValue(dt, [(IntValue(5), BoolValue(True))])])
    assert values_equal(tuple_value, tuple_value)


def test_int_value_to_string():
    assert IntValue(5).to_string() == "5"


def test_bool_value_to_string():
    assert BoolValue(True).to_string() == "true"


def test_char_value_to_string():
    assert CharValue("a").to_string() == "a"


def test_string_value_to_string():
    assert StringValue("test").to_string() == "test"


def test_none_value_to_string():
    assert NoneValue().to_string() == "none"


def test_list_value_to_string():
    assert ListValue(ListType(IntType()), [IntValue(5), IntValue(4)]).to_string() == "[5, 4]"


def test_tuple_value_to_string():
    assert TupleValue(TupleType([IntType(), BoolType()]), [IntValue(5), BoolValue(True)]).to_string() == "(5, true)"


def test_dict_value_to_string():
    value = (IntValue(5), BoolValue(True))
    assert DictValue(DictType(key_type=IntType(), value_type=BoolType()), [value, value]).to_string() == "[5: true, 5: true]"


def test_schema_value_to_string():
    st = SchemaType()
    st.column_types = [IntType(), BoolType(), StringType()]
    schema_value = SchemaValue(st, [(StringValue("a"), IntType()), (StringValue("b"), BoolType()), (StringValue("c"), StringType())])
    assert schema_value.to_string() == "${a: int, b: bool, c: string}"


def test_table_value_to_string():
    st = SchemaType()
    st.column_types = [IntType(), BoolType(), StringType()]
    schema_value = SchemaValue(st, [(StringValue("a"), IntType()), (StringValue("b"), BoolType()), (StringValue("c"), StringType())])
    tbt = TableType()
    tbt.schema_type = st
    row_type = TupleType(st.column_types)
    row1 = TupleValue(row_type, [IntValue(5), BoolValue(True), StringValue("test")])
    row2 = TupleValue(row_type, [IntValue(4), BoolValue(False), StringValue("test2")])
    table_value = TableValue(tbt, schema_value, [row1, row2])
    assert table_value.to_string() == """\x1b[4m                        \n\x1b[1m| int | bool  | string |\n| a   | b     | c      |\n\x1b[0m\x1b[4m| 5   | true  | test   |\n\x1b[0m\x1b[4m| 4   | false | test2  |\n\x1b[0m"""


def test_func_value_to_string_not_builtin():
    ft = FuncType()
    ft.parameter_types = [IntType(), BoolType()]
    ft.return_type = IntType()
    parameters = [("p1", IntType()), ("p2", BoolType())]
    lit_exp = LitExpression()
    lit_exp.literal = IntLiteral(5)
    func_value = FuncValue(ft, None, parameters, lit_exp, None)
    assert func_value.to_string() == "(p1: int, p2: bool) -> int"


def test_func_value_to_string_builtin():
    assert src.builtins.io_petl_builtins.PrintLn().to_value().to_string() == "builtin:println(value: any) -> none"
