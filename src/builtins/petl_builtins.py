from typing import Dict

from src.builtins.petl_builtin_definitions import *
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
    # List/Dict
    Keyword.ZIP.value: Zip(),
    # "insert": Insert(),
    # "remove": Remove(),
    # "replace": Replace(),
    # "front": Front(),
    # "back": Back(),
    # "head": Head(),
    # "tail": Tail(),
    # "isEmpty": IsEmpty(),
    # "contains": Contains(),
    # "find": Find(),
    # "fill": Fill(),
    # "reverse": Reverse(),
    # "set": Set(),
    # "intersect": Intersect(),
    # end List/Dict
    # ----------------------------------------
    # String
    Keyword.SLICE.value: Slice(),
    Keyword.SUBSTR.value: Substr(),
    Keyword.LEN.value: Len(),
    Keyword.TYPE.value: Type(),
    Keyword.TOSTR.value: ToStr(),
    # "toCharList": toCharList(),
    # end String
    # ----------------------------------------
    # Integer
    Keyword.TOINT.value: ToInt(),
    # "sum": Sum(),
    # "product": Product(),
    # "max": Max(),
    # "min": Min(),
    # "sort": Sort(),
    # end Integer
    # -----------------------------------------
    # Table
    Keyword.CREATETABLE.value: CreateTable(),
    Keyword.READCSV.value: ReadCsv(),
    # "writeCsv": WriteCsv(),
    # "join": Join(),
    # "with": With(),
    # "where": Where(),
    # "select": Select(),
    # "drop": Drop(),
    # "column": Column(),
    # "collect": Collect(),
    # "count": Count()
    # end Table
    # ----------------------------------------
    # Other
    # "halt": Halt(),
    # "equals": Equals(),
    # "rand": Rand()
    # end Other
}


def get_builtin(name: str) -> Builtin:
    return _builtins[name]
