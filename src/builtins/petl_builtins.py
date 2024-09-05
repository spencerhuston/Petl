from typing import Dict

from src.builtins.functional_petl_builtins import *
from src.builtins.int_petl_builtins import *
from src.builtins.io_petl_builtins import *
from src.builtins.iterable_petl_builtins import *
from src.builtins.list_petl_builtins import *
from src.builtins.misc_petl_builtins import *
from src.builtins.string_petl_builtins import *
from src.builtins.table_petl_builtins import *
from src.tokens.petl_keyword import Keyword

_builtins: Dict[str, Builtin] = {
    # IO
    Keyword.READLN.value: ReadLn(),
    Keyword.PRINT.value: Print(),
    Keyword.PRINTLN.value: PrintLn(),
    # end IO
    # ----------------------------------------
    # Functional
    Keyword.MAP.value: Map(),
    Keyword.FILTER.value: Filter(),
    Keyword.FOLDL.value: Foldl(),
    Keyword.FOLDR.value: Foldr(),
    # end Functional
    # ----------------------------------------
    # Iterable
    Keyword.ZIP.value: Zip(),
    Keyword.LEN.value: Len(),
    Keyword.ISEMPTY.value: IsEmpty(),
    # end Iterable
    # ----------------------------------------
    # List
    Keyword.INSERT.value: Insert(),
    Keyword.REMOVE.value: Remove(),
    Keyword.REPLACE.value: Replace(),
    Keyword.FRONT.value: Front(),
    Keyword.BACK.value: Back(),
    Keyword.HEAD.value: Head(),
    Keyword.TAIL.value: Tail(),
    Keyword.SLICE.value: Slice(),
    Keyword.CONTAINS.value: Contains(),
    Keyword.FIND.value: Find(),
    Keyword.FILL.value: Fill(),
    Keyword.REVERSE.value: Reverse(),
    Keyword.SET.value: Set(),
    Keyword.INTERSECT.value: Intersect(),
    # end List
    # ----------------------------------------
    # String
    Keyword.SUBSTR.value: Substr(),
    Keyword.TOSTR.value: ToStr(),
    Keyword.TOUPPER.value: ToUpper(),
    Keyword.TOLOWER.value: ToLower(),
    Keyword.STARTSWITH.value: StartsWith(),
    Keyword.ENDSWITH.value: EndsWith(),
    # end String
    # ----------------------------------------
    # Integer
    Keyword.TOINT.value: ToInt(),
    Keyword.SUM.value: Sum(),
    Keyword.PRODUCT.value: Product(),
    Keyword.MAX.value: Max(),
    Keyword.MIN.value: Min(),
    Keyword.SORT.value: Sort(),
    # end Integer
    # -----------------------------------------
    # Table
    Keyword.CREATETABLE.value: CreateTable(),
    Keyword.READCSV.value: ReadCsv(),
    Keyword.WRITECSV.value: WriteCsv(),
    Keyword.JOIN.value: Join(),
    Keyword.WITH.value: With(),
    Keyword.WHERE.value: Where(),
    Keyword.SELECT.value: Select(),
    Keyword.DROP.value: Drop(),
    Keyword.COLUMN.value: Column(),
    Keyword.COLLECT.value: Collect(),
    Keyword.COUNT.value: Count(),
    # end Table
    # ----------------------------------------
    # Other
    Keyword.TYPE.value: Type(),
    Keyword.RAND.value: Rand()
    # end Other
}


def get_builtin(name: str) -> Builtin:
    return _builtins[name]
