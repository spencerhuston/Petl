bird operator)

## Lambdas

---

Lambdas are Petl's only function-type and are first-class. They are never declared or 
put into scope alone, requiring that they be assigned to a variable or passed to 
another lambda or builtin function directly as a value. Parameters are optional but require
a type-hint. Likewise the return type is required in the declaration.

Lambdas also capture their current global scope, allowing them to act as closures and in turn
providing functionality of something akin to currying and/or partial application. **Note**,
due to the method in which scope is acquired, mutual recursion between lambdas is _not_
supported.

#### Syntax
```
| [<parameter>: <type>[, <parameter>: <type>]] | -> <type> { <body> }
```

#### Declaration examples and type-hints
Lambda type hints include both parameter types (enclosed in parenthesis if more or less than 
exactly 1), and the return type. Lambdas with function return types must be chained together.
```
 # int -> int (equally valid is (int) -> int)
let f = |x: int| -> int { x + 2 };

 # () -> int
let f2 = || -> int { 5 };

 # (int, int) -> int -> int or (int, int) -> (int) -> int
let f3 = |x: int, y: int| -> int -> int { 
    |z: int| -> int { x + y + z } 
};
```

---

## Bird operator

Being that data manipulation is a large focus in Petl, the language offers a builtin
function composition operator, ```|>```, that acts as an equivalent to ```andThen```
in a language like Scala. It is purely syntactic sugar, done by allowing the first
argument of a function to precede the function call itself before the operator. **Note** that
if a function only has 1 argument the function can be called with _or_ without parenthesis.
A function with zero parameters cannot be called with the operator.

#### Examples
```
let is_even = |x: int| -> bool { x % 2 == 0 };
let double = |x: int| -> int { x * 2 };

[1, 2, 3, 4] |> filter(is_even) |> map(double)
```
versus the traditional syntax
```
map(filter([1, 2, 3, 4], is_even), double)
```
Result ```[4, 8]```
<br><br>

Chaining to a 1-parameter function or lambda
```
[1, 2, 3, 4] |> filter(is_even) |> map(double) |> println
```
or
```
[1, 2, 3, 4] |> filter(is_even) |> map(double) |> println()
```