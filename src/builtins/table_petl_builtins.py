import csv

from src.builtins.petl_builtin_definitions import Builtin
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

            def header_matches_schema(header_row: List[str], schema_value: SchemaValue) -> bool:
                return all(map(lambda h, sv: h == sv[0], header_row, schema_value.values))

            # def row_matches_schema(row: List[str], schema_value: SchemaValue) -> bool:
            #     for value in row:
            #         if types_conform()

            with open(path_value.value + ".csv", mode ='r') as csv_file:
                csv_file_rows: List[List[str]] = list(csv.reader(csv_file))
                if isinstance(schema_value.petl_type, SchemaType):
                    rows: ListValue = ListValue(ListType(TupleType(schema_value.petl_type.column_types)), [])
                    if csv_file_rows:
                        if header_value.value:
                            header_row: List[str] = csv_file_rows[0]
                            if not header_matches_schema(header_row, schema_value):
                                error(f"Provided schema does not match CSV header: {header_row}", application.token)
                                return NoneValue()

                        for row in csv_file_rows:
                            pass


                #else return empty table value

        return NoneValue()


class WriteCsv:
    pass


class Join:
    pass


class With:
    pass


class Where:
    pass


class Select:
    pass


class Drop:
    pass


class Column:
    pass


class Collect:
    pass


class Count:
    pass
