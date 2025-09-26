## Flow Control

---

### If-else statements

#### Syntax
```
if (<condition>) { <statement> } [else { <statement> }]
```
As stated in the [variables](variables_and_prims.md) section, all statements implicitly 
return a value, including ```if's```. Due to the ```else``` block being-optional, 
if only the ```if```is present, the entire statement will return a ```none``` type.

#### Examples
```
let a = 5;
if (a == 6) { "failed" } else { "succeeded" }
```
Returns ```"failed"```
<br><br>
```
let a = 5;
if (a == 6) { "failed" }
```
Returns ```none```
<br><br>
This allows them to be easily embedded in operations like ```map```.
```
[1, 2, 3, 4] |> map(|x: int| -> int { if (x % 2 == 0) { x / 2 } else { x } }
```
Returns ```[1, 1, 3, 2]```

---
## For-loops

#### Syntax
```
for <iterator name> in <iterable statement> {
    <statement>
}
```

Petl ```for```-loops are side-effect only, meaning they have no return value 
(implicitly return ```none```). **Note** that the iterator can only be constructed by the 
```<iterable statement>```, which must return an [iterable-type](collections.md).

#### Examples

##### List
```
for i in [0, 1, 2, 3, 4, 5] {
    print(i)
}
```
Prints 
```012345```
<br><br>

##### Range
```
for i in 0~5 {
    println(i)
}
```
Prints
```012345```
<br><br>

##### Tuple
```
for i in ('a', 1, false) {
    println(i)
}
```
Prints
```
a
1
false
```
<br><br>

##### Dictionary
```
let d = ['a': 1, 'b': 2];
for key in d {
    let i = d(key);
    println(i)
}
```
Prints
```
a
2
```