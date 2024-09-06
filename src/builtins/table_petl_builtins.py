import csv
from copy import deepcopy

from src.builtins.petl_builtin_definitions import Builtin, from_string_value
from src.phases.environment import InterpreterEnvironment
from src.phases.type_resolver import types_conform
from src.semantic_defintions.petl_expression import Application
from src.semantic_defintions.petl_value import *
from src.tokens.petl_keyword import Keyword


class CreateTable(Builtin):
    def __init__(self):
        parameters = [
            ("schema", SchemaType()),
            ("rows", ListType(TupleType()))
        ]
        Builtin.__init__(self, Keyword.CREATETABLE.value, parameters, TableType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        schema_value: PetlValue = environment.get("schema", application.token, error)
        rows_value: PetlValue = environment.get("rows", application.token, error)
        if isinstance(schema_value, SchemaValue) and isinstance(rows_value, ListValue):
            schema_values: List[Tuple[PetlValue, PetlType]] = schema_value.values
            rows: List[PetlValue] = rows_value.values
            for row in rows:
                if isinstance(row, TupleValue):
                    tuple_value: TupleValue = row
                    zipped_tuple_schema_values = list(map(lambda tv, sv: (tv, sv), tuple_value.values, schema_values))
                    for value, column in zipped_tuple_schema_values:
                        if not types_conform(application.token, value.petl_type, column[1], error):
                            return NoneValue()
            if isinstance(schema_value.petl_type, SchemaType):
                return TableValue(TableType(SchemaType(schema_value.petl_type.column_types)), schema_value, rows)
        return NoneValue()


class ReadCsv(Builtin):
    def __init__(self):
        parameters = [
            ("path", StringType()),
            ("header", BoolType()),
            ("schema", SchemaType())
        ]
        Builtin.__init__(self, Keyword.READCSV.value, parameters, TableType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        path_value: PetlValue = environment.get("path", application.token, error)
        header_value: PetlValue = environment.get("header", application.token, error)
        schema_value: PetlValue = environment.get("schema", application.token, error)

        if isinstance(path_value, StringValue) and isinstance(header_value, BoolValue) and isinstance(schema_value, SchemaValue):
            path_value: StringValue = path_value
            header_value: BoolValue = header_value
            schema_value: SchemaValue = schema_value

            def header_matches_schema_names(header_row: List[str], schema_value: SchemaValue) -> bool:
                return all(map(lambda h, sv: h == sv[0].value, header_row, schema_value.values))

            def row_matches_schema(row: List[PetlValue], schema_value: SchemaValue) -> bool:
                return all(map(lambda value, column: types_conform(application.token, value.petl_type, column[1], error), row, schema_value.values))

            with open(path_value.value + ".csv", mode ='r') as csv_file:
                csv_file_rows: List[List[str]] = list(csv.reader(csv_file))
                if isinstance(schema_value.petl_type, SchemaType):
                    row_type: TupleType = TupleType(schema_value.petl_type.column_types)
                    rows: List[PetlValue] = []
                    if csv_file_rows:
                        if header_value.value:
                            header_row: List[str] = csv_file_rows[0]
                            if not header_matches_schema_names(header_row, schema_value):
                                error(f"Provided schema does not match CSV header: {header_row}", application.token)
                                return NoneValue()

                        for row in csv_file_rows[1 if header_value.value else 0:]:
                            petl_value_row: List[PetlValue] = list(map(lambda v: from_string_value(v), row))
                            if row_matches_schema(petl_value_row, schema_value):
                                rows.append(TupleValue(row_type, petl_value_row))

                        return TableValue(TableType(schema_value.petl_type), schema_value, rows)
        return NoneValue()


class WriteCsv(Builtin):
    def __init__(self):
        parameters = [
            ("table", TableType()),
            ("header", BoolType())
        ]
        Builtin.__init__(self, Keyword.WRITECSV.value, parameters, NoneType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        table_value: PetlValue = environment.get("table", application.token, error)
        return NoneValue()


class Join:
    pass


class With:
    pass


class Where:
    pass


class Select:
    pass


class Drop(Builtin):
    def __init__(self):
        parameters = [
            ("table", TableType()),
            ("column", StringType())
        ]
        Builtin.__init__(self, Keyword.DROP.value, parameters, TableType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        table_value: PetlValue = environment.get("table", application.token, error)
        column_value: PetlValue = environment.get("column", application.token, error)
        if isinstance(table_value, TableValue) and isinstance(column_value, StringValue):
            column_value: StringValue = column_value
            column_index: int = next(i for i, sv in enumerate(table_value.schema.values) if values_equal(sv[0], column_value))
            dropped_table_schema: SchemaValue = deepcopy(table_value.schema)
            dropped_table_schema.values.pop(column_index)
            if isinstance(dropped_table_schema.petl_type, SchemaType):
                dropped_table_schema.petl_type.column_types.pop(column_index)

            if isinstance(table_value.petl_type, TableType):
                table_type: TableType = table_value.petl_type
                table_type.schema_type.column_types.pop(column_index)

                table_rows: List[PetlValue] = []
                row_type: TupleType = TupleType(table_type.schema_type.column_types)
                for row in table_value.rows:
                    if isinstance(row, TupleValue):
                        dropped_row: TupleValue = TupleValue(row_type, row.values)
                        dropped_row.values.pop(column_index)
                        table_rows.append(dropped_row)
                return TableValue(table_type, dropped_table_schema, table_rows)
        return NoneValue()


class Column:
    pass


class Collect(Builtin):
    def __init__(self):
        parameters = [
            ("table", TableType())
        ]
        Builtin.__init__(self, Keyword.COLLECT.value, parameters, ListType(TupleType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        table_value: PetlValue = environment.get("table", application.token, error)
        if isinstance(table_value, TableValue) and isinstance(table_value.schema.petl_type, SchemaType):
            return ListValue(ListType(TupleType(table_value.schema.petl_type.column_types)), table_value.rows)
        return NoneValue()


class Count(Builtin):
    def __init__(self):
        parameters = [
            ("table", TableType())
        ]
        Builtin.__init__(self, Keyword.COUNT.value, parameters, IntType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        table_value: PetlValue = environment.get("table", application.token, error)
        if isinstance(table_value, TableValue):
            return IntValue(len(table_value.rows))
        return NoneValue()
