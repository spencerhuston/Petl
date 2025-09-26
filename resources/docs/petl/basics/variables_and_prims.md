## Primitive Types

---

Petl has the following primitives:
- ```int``` Integer type
- ```bool``` Boolean type, either ```true``` or ```false```
- ```char``` Char type, literals denoted as ```'{character}'```
- ```string``` String type, literals denoted as ```"{string}"```
  * Supports indexing to a reference, but not literals.
  <br>```let a = "test"; a(0) == 't'``` is valid, but ```"test"(0)``` is not
  * ```string```-type exclusive [builtin functions](../builtin/string.md)
- ```none``` None type, holds no value

---

## Declaring variables

Petl variables are immutable only, meaning the value _cannot_ be changed once the 
variable is created. However, they can be redeclared and shadow the previous 
variable in a new scope. Likewise, _all_ statements that do not end in ```;``` 
will implicitly return a value. 

To declare a variable, use the following syntax. Types are inferred.
```
let a = 5
```

To declare with a type hint (this will implicitly return a value of ```5```)
```
let a: int = 5;
let b: char = 'b';
a
```

Shadowing
```
let a = 5;
let b = a + 4; # 9
let a = 3;
let b = a + 4 # 7
```
