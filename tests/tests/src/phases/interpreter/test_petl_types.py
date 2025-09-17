from petllang.phases.interpreter.definitions.types import _type_list_to_string, IntType, BoolType, UnionType, ListType, TupleType, \
    DictType, SchemaType, TableType, FuncType


def test_type_list_to_string():
    assert _type_list_to_string("list", [IntType(), BoolType()])


def test_union_type_to_string():
    ut = UnionType()
    ut.union_types = [IntType(), BoolType()]
    assert ut.to_string() == "union[int, bool]"


def test_list_type_to_string():
    assert ListType(IntType()).to_string() == "list[int]"


def test_tuple_type_to_string():
    tt = TupleType()
    tt.tuple_types = [IntType(), BoolType()]
    assert tt.to_string() == "tuple[int, bool]"


def test_dict_type_to_string():
    dt = DictType()
    dt.key_type = IntType()
    dt.value_type = BoolType()
    assert dt.to_string() == "dict[int:bool]"


def test_schema_type_to_string():
    st = SchemaType()
    st.column_types = [IntType(), BoolType(), IntType()]
    assert st.to_string() == "schema[int, bool, int]"


def test_table_type_to_string():
    tbt = TableType()
    st = SchemaType()
    st.column_types = [IntType(), BoolType(), IntType()]
    tbt.schema_type = st
    assert tbt.to_string() == "table[schema[int, bool, int]]"


def test_func_type_to_string():
    ft = FuncType()
    ft.parameter_types = [IntType(), BoolType()]
    ft.return_type = IntType()
    assert ft.to_string() == "(int, bool) -> int"
