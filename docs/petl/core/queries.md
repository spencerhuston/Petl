## Petl Query Language (PQL)

---

PQL was born out of a necessity to directly compare two values in the combined row
from 1 or more tables, namely for ```join``` and ```select``` operations. PQL is a
lightweight query language created to provide that, allowing for normal binary primitive
operations among 1 or more values in a given row. The grammar for PQL be found 
[here](../../grammars.md).

---

### Support
1. All literal values in Petl (minus ```none```)
2. All boolean and arithmetic operators available in Petl
3. Ranges
4. ```in``` operator for checking if an ```int``` value lives in a given ```range```
5. Variable references
   1. References are populated for a given row using the provided list of column 
   names
   2. Therefore, references used in a PQL query must exist in the columns listed for the given
   ```join``` or ```select``` call
   3. Resultant column names list cannot have duplicates
   4. For ```join``` calls, listed column names from the first listed table must have ```left.```
   appended to the front. Calls from the second table must have ```right.```. This ensures any
   column names that overlap between the two tables are correctly referenced

###### Note: String literals in queries are currently broken

#### Example
```
let t1 = createTable(
    ${
        name: string,
        age: int,
        salary: string
    },
    [("Alice", 27, "$60000"),
     ("Bob", 45, "$100000"),
     ("Mark", 23, "$45000")]
);

let t2 = createTable(
    ${
        name: string,
        state: string
    },
    [("Bob", "Idaho"),
     ("Jack", "California"),
     ("Alice", "Texas"),
     ("Henry", "Indiana")]
);

t1
|> join(t2, ["left.name", "left.age", "right.state"], "left.name == right.name and left.age in 25~45"))
|> select(["name"], "state == "Texas" or age == 27")
|> collect()
|> println()
```
Prints ```[Alice]```