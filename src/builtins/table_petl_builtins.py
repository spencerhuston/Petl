import csv
import os
from copy import deepcopy
from pathlib import Path
from typing import Dict, Optional

from src.builtins.builtin_definitions import Builtin, from_string_value
from src.phases.interpreter.definitions.value import *
from src.phases.interpreter.environment import InterpreterEnvironment
from src.phases.interpreter.type_resolution import types_conform
from src.phases.lexer.definitions.keyword import Keyword
from src.phases.parser.defintions.expression import Application
from src.query.executor import execute_query


# Join and Select helper functions #
def get_selected_indices(table_columns: List[Tuple[StringValue, PetlType]],
                         selected_columns: List[str],
                         table_name: Optional[str] = None) -> Dict[int, Tuple[str, PetlType]]:
    valid_columns: Dict[int, Tuple[str, PetlType]] = {}
    for index, table_column in enumerate(table_columns):
        table_column_name = f"{table_name}.{table_column[0].value}" if table_name else table_column[0].value
        if table_column_name in selected_columns:
            valid_columns[index] = (table_column_name, table_column[1])
    return valid_columns


def add_variable_to_query_environment(table_columns: List[Tuple[StringValue, PetlType]],
                                      row: PetlValue,
                                      table_name: Optional[str] = None) -> List[Tuple[str, PetlValue]]:
    variables = []
    if isinstance(row, TupleValue):
        for (column_name, column_type), columns_value in zip(table_columns, row.values):
            variables.append((f"{table_name}.{column_name.value}" if table_name else column_name.value, columns_value))
    return variables


def get_selected_values(indices: Dict[int, Tuple[str, PetlType]],
                        row: List[PetlValue]) -> List[PetlValue]:
    selected_values: List[PetlValue] = []
    for index, value in enumerate(row):
        if index in indices:
            selected_values.append(value)
    return selected_values


def get_column_types(table_column_indices: Dict[int, Tuple[str, PetlType]]) -> List[PetlType]:
    return list(map(lambda k: table_column_indices[k][1], table_column_indices))


def get_columns(table_column_indices: Dict[int, Tuple[str, PetlType]]) -> List[Tuple[StringValue, PetlType]]:
    return list(map(lambda k: (StringValue(table_column_indices[k][0]), table_column_indices[k][1]), table_column_indices))
# end helper functions #


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

        if isinstance(path_value, StringValue) and isinstance(header_value, BoolValue) and isinstance(schema_value,
                                                                                                      SchemaValue):
            path_value: StringValue = path_value
            header_value: BoolValue = header_value
            schema_value: SchemaValue = schema_value

            def header_matches_schema_names(header_row: List[str], schema_value: SchemaValue) -> bool:
                return all(map(lambda h, sv: h == sv[0].value, header_row, schema_value.values))

            def row_matches_schema(row: List[PetlValue], schema_value: SchemaValue) -> bool:
                return all(
                    map(lambda value, column: types_conform(application.token, value.petl_type, column[1], error), row,
                        schema_value.values))

            try:
                path = Path(path_value.value + ".csv")
                with open(path, mode='r') as csv_file:
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
            except Exception as read_csv_exception:
                error(f"Failed to read CSV: {path_value.value}: {read_csv_exception}", application.token)
        return NoneValue()


class WriteCsv(Builtin):
    def __init__(self):
        parameters = [
            ("path", StringType()),
            ("table", TableType()),
            ("header", BoolType())
        ]
        Builtin.__init__(self, Keyword.WRITECSV.value, parameters, BoolType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        path_value: PetlValue = environment.get("path", application.token, error)
        table_value: PetlValue = environment.get("table", application.token, error)
        header_value: PetlValue = environment.get("header", application.token, error)
        if isinstance(path_value, StringValue) and isinstance(table_value, TableValue) and isinstance(header_value,
                                                                                                      BoolValue):
            header = []
            if header_value.value:
                header = [v[0].value for v in table_value.schema.values]
            rows = []
            for row in table_value.rows:
                if isinstance(row, TupleValue):
                    rows.append(list(map(lambda v: v.value, row.values)))
            try:
                path = Path(path_value.value + ".csv")
                with open(path, "w", newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    if header:
                        csv_writer.writerow(header)
                    csv_writer.writerows(rows)
                if os.path.exists(path):
                    return BoolValue(True)
                else:
                    error(f"Failed to write CSV: {path}, unknown reason", application.token)
            except Exception as write_csv_exception:
                error(f"Failed to write CSV: {path_value.value}: {write_csv_exception}", application.token)
        return NoneValue()


class Join(Builtin):
    def __init__(self):
        parameters = [
            ("left_table", TableType()),
            ("right_table", TableType()),
            ("columns", ListType(StringType())),
            ("where", StringType())
        ]
        Builtin.__init__(self, Keyword.JOIN.value, parameters, TableType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        left_table_value: PetlValue = environment.get("left_table", application.token, error)
        right_table_value: PetlValue = environment.get("right_table", application.token, error)
        columns_value: PetlValue = environment.get("columns", application.token, error)
        where_value: PetlValue = environment.get("where", application.token, error)

        if isinstance(left_table_value, TableValue) and isinstance(right_table_value, TableValue) \
                and isinstance(columns_value, ListValue) and isinstance(where_value, StringValue):
            selected_columns = list(map(lambda c: c.value, columns_value.values))
            left_table_column_indices = get_selected_indices(left_table_value.schema.values, selected_columns, "left")
            right_table_column_indices = get_selected_indices(right_table_value.schema.values, selected_columns, "right")
            columns_types = get_column_types(left_table_column_indices) + get_column_types(right_table_column_indices)

            joined_rows: List[TupleValue] = []
            for left_row in left_table_value.rows:
                left_variables = add_variable_to_query_environment(left_table_value.schema.values, left_row, "left")
                for right_row in right_table_value.rows:
                    all_variables = left_variables + add_variable_to_query_environment(right_table_value.schema.values, right_row, "right")
                    if execute_query(where_value.value, all_variables, application.token, error):
                        if isinstance(left_row, TupleValue) and isinstance(right_row, TupleValue):
                            joined_row_values = [*get_selected_values(left_table_column_indices, left_row.values),
                                                 *get_selected_values(right_table_column_indices, right_row.values)]
                            joined_rows.append(TupleValue(TupleType(columns_types), joined_row_values))

            st = SchemaType(columns_types)
            schema = SchemaValue(st, get_columns(left_table_column_indices) + get_columns(right_table_column_indices))

            tbt = TableType(st)
            joined_table = TableValue(tbt, schema, joined_rows)
            return joined_table

        return NoneValue()


class With(Builtin):
    def __init__(self):
        parameters = [
            ("table", TableType()),
            ("name", StringType()),
            ("values", ListType(AnyType()))
        ]
        Builtin.__init__(self, Keyword.WITH.value, parameters, TableType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        table_value: PetlValue = environment.get("table", application.token, error)
        name_value: PetlValue = environment.get("name", application.token, error)
        values_value: PetlValue = environment.get("values", application.token, error)
        if isinstance(table_value, TableValue) and isinstance(name_value, StringValue) and isinstance(values_value,
                                                                                                      ListValue):
            new_column_value_count = len(values_value.values)
            if new_column_value_count == 0:
                error(f"New column \'{name_value.value}\' must contain values to be added to table", application.token)
                return NoneValue()

            row_count = len(table_value.rows)
            if new_column_value_count != row_count:
                error(
                    f"New column \'{name_value.value}\' must contain same number of rows ({row_count}) to be added to table",
                    application.token)
                return NoneValue()

            new_column_type = values_value.values[0].petl_type
            if isinstance(table_value.schema.petl_type, SchemaType):
                table_value.schema.petl_type.column_types.append(new_column_type)
            if isinstance(table_value.petl_type, TableType):
                table_value.petl_type.schema_type.column_types.append(new_column_type)

            for value, row in zip(values_value.values, table_value.rows):
                if isinstance(row.petl_type, TupleType):
                    row.petl_type.tuple_types.append(new_column_type)
                if isinstance(row, TupleValue):
                    row.values.append(value)
            return table_value
        return NoneValue()


class Select(Builtin):
    def __init__(self):
        parameters = [
            ("table", TableType()),
            ("columns", ListType(StringType())),
            ("where", StringType())
        ]
        Builtin.__init__(self, Keyword.SELECT.value, parameters, TableType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        table_value: PetlValue = environment.get("table", application.token, error)
        columns_value: PetlValue = environment.get("columns", application.token, error)
        where_value: PetlValue = environment.get("where", application.token, error)

        if isinstance(table_value, TableValue) and isinstance(columns_value, ListValue) and isinstance(where_value, StringValue):
            selected_columns = list(map(lambda c: c.value, columns_value.values))
            table_column_indices = get_selected_indices(table_value.schema.values, selected_columns)
            columns_types = get_column_types(table_column_indices)

            joined_rows: List[TupleValue] = []
            for row in table_value.rows:
                variables = add_variable_to_query_environment(table_value.schema.values, row)
                if execute_query(where_value.value, variables, application.token, error):
                    if isinstance(row, TupleValue):
                        joined_row_values = get_selected_values(table_column_indices, row.values)
                        joined_rows.append(TupleValue(TupleType(columns_types), joined_row_values))

            st = SchemaType(columns_types)
            schema = SchemaValue(st, get_columns(table_column_indices))

            tbt = TableType(st)
            joined_table = TableValue(tbt, schema, joined_rows)
            return joined_table


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
            column_index = -1
            for index, (column_name, column_type) in enumerate(table_value.schema.values):
                if column_name.value == column_value.value:
                    column_index = index
            if column_index == -1:
                error(f"Column \'{column_value.value}\' does not exist in this table", application.token)
                return NoneValue()

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


class Columns(Builtin):
    def __init__(self):
        parameters = [
            ("table", TableType()),
            ("names", ListType(StringType()))
        ]
        Builtin.__init__(self, Keyword.COLUMNS.value, parameters, TableType())

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        table_value: PetlValue = environment.get("table", application.token, error)
        names_value: PetlValue = environment.get("names", application.token, error)
        if isinstance(table_value, TableValue) and isinstance(names_value, ListValue):
            column_names = list(map(lambda t: t[0].value, table_value.schema.values))
            for name in names_value.values:
                if isinstance(name, StringValue) and name.value not in column_names:
                    error(f"Column \'{name.value}\' does not exist in this table", application.token)
                    return NoneValue()

            columns = []
            column_indices = []
            for index, (column_name, column_type) in enumerate(table_value.schema.values):
                for name in names_value.values:
                    if isinstance(name, StringValue) and name.value == column_name.value:
                        columns.append((name, column_type))
                        column_indices.append(index)
            st = SchemaType(list(map(lambda c: c[1], columns)))
            schema = SchemaValue(st, columns)
            rows = []
            for row in table_value.rows:
                if isinstance(row, TupleValue):
                    rows.append(TupleValue(TupleType(st.column_types),
                                           [v for index, v in enumerate(row.values) if index in column_indices]))
            return TableValue(TableType(st), schema, rows)
        return NoneValue()


class Column(Builtin):
    def __init__(self):
        parameters = [
            ("table", TableType()),
            ("name", StringType())
        ]
        Builtin.__init__(self, Keyword.COLUMN.value, parameters, ListType(TupleType()))

    def evaluate(self, application: Application, environment: InterpreterEnvironment, interpreter, error) -> PetlValue:
        table_value: PetlValue = environment.get("table", application.token, error)
        string_value: PetlValue = environment.get("name", application.token, error)
        if isinstance(table_value, TableValue) and isinstance(string_value, StringValue):
            column_type: PetlType = UnknownType()
            column_index = -1
            for index, (cn, ct) in enumerate(table_value.schema.values):
                if string_value.value == cn.value:
                    column_type = ct
                    column_index = index
            if isinstance(column_type, UnknownType):
                error(f"Column \'{string_value.value}\' does not exist in this table", application.token)
                return NoneValue()

            column_values = []
            for row in table_value.rows:
                if isinstance(row, TupleValue):
                    column_values.append(row.values[column_index])

            return ListValue(ListType(column_type), column_values)
        return NoneValue()


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
