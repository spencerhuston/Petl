## Table-type builtins

---

```createTable(s: schema, r: list[tuple[...]]) -> table```<br>
Creates a new ```table``` with the given schema ```s``` and rows ```r```

---

```readCsv(p: string, header: bool, s: schema) -> table```<br>
Reads the CSV at path ```p``` and creates a new ```table``` according to schema ```s```
if ```header``` is ```false``` or against the CSV's header row. **Note** that the file
path ```p``` is relative to the interpreter's working directory

---

```writeCsv(p: string, t: table, header: bool) -> bool```<br>
Writes table ```t``` to path ```p```. Includes header row from schema-value from ```t```
if ```header``` is ```true```. **Note** that the file path ```p``` is relative 
to the interpreter's working directory

---

```join(t1: table, t2: table, cs: list[string], q: string) -> table```<br>
Creates a new ```table``` from the inner-join of tables ```t1``` and ```t2```

**Notes**
1. Only the columns listed in ```cs``` are kept
2. Only rows that are intersected _and_ pass the PQL query ```q``` are kept

---

```with(t: table, name: string, vs: list[any]) -> table```<br>
Adds a new column of name ```name``` and values ```vs``` to table ```t```

---

```select(t: table, cs: list[string], q: string) -> table```<br>
Selects one or more columns in list ```cs``` that pass the PQL query ```q```

---

```drop(t: table, c: string) -> table```<br>
Removes column of name ```c``` from table ```t```

---

```columns(t: table, cs: list[string]) -> table```<br>
Returns a subset of table ```t``` with only columns ```cs```. 
Like ```select``` but with no query

---

```column(t: table, c: string) -> list[any]```<br>
Returns values of column of name ```c``` from table ```t``` as a ```list```

---

```collect(t: table) -> list[tuple[...]]```<br>
Returns ```t``` as a ```list``` of ```tuple```

---

```count(t: table) -> int```<br>
Returns the number of rows of table ```t``` as an ```int```