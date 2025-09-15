## Tables and Schemas

---

### Tables
```table```-types are a core, first-class feature of Petl that allows for the direct 
manipulation of the contents of CSV-formatted data. **Note** that nullability is
currently not supported.

There are 2 ways of creating a ```table```-value, both of them being 
[builtin functions](../builtin/table.md) and both requiring a 
```schema```-value, covered below:
1. ```createTable```
2. ```readCsv```

All other operations on a ```table``` require the use of the other builtin functions.
Under the hood they are implemented as a combination of:
1. Meta-data in the form of the ```schema```. Just a list of the column names 
and their types
2. Rows, which are formed as a ```list``` of ```tuple```. The ```tuple```-type will
always match the types provided in the ```schema```

#### Example
```
let s = ${
        name: string,
        age: int,
        salary: string
    };
    
let t = createTable(
    s,
    [("Alice", 27, "$60,000"),
     ("Bob", 45, "$100,000"),
     ("Mark", 23, "$45,000")]
);

let is_digit = |c: char| -> bool {
    match c {
        case '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' => true,
        case _ => false
    }
};

let format_salary = |salary: string| -> string {
    salary |> filter(is_digit) |> toInt
};

let salaries = t |> column("salary") |> map(format_salary);
println(salaries)
```
Prints ```[60000, 100000, 45000]```

---

### Schemas

Schemas are simply a list of the names of columns and their types, but not for a specific
```table```. A schema can be used for any number of ```table```-values that all should
have identical formatting. At least one column name/type pair is required.

#### Syntax
```
${
    <name>: <type>[,
    <name2>:<type2>,
    ...]
}
```

#### Example
```
let employee_schema = ${
    name: string,
    age: int,
    salary: string
};

let t1 = createTable(
    employee_schema,
    [("Alice", 27, "$60,000"),
     ("Bob", 45, "$100,000"),
     ("Mark", 23, "$45,000")]
);

let t2 = createTable(
    employee_schema,
    [("John", 25, "$55,000"),
     ("Mary", 35, "$75,000")]
);
```