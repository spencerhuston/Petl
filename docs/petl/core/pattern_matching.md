## Pattern-matching
Another core feature of Petl is the ability to pattern-match. Petl supports pattern-matching
via:
- type - If the value is of the listed type
- predicate - If the value is of the listed type and passes a condition
- multiple literals - If the value exists in a list of literals
- ranges - If the value exists in an integer list
- wildcard - Anything matches

**Notes**: 
1. If no valid case is matched, an error will be thrown. Include a wildcard, ```_```, 
at the bottom as a catch-all
2. Cases are evaluated top to bottom. Therefore, if more than one case is valid, the first
one listed will be evaluated
3. The return type of each case statement must match across all cases
4. The ```if```-statement is evaluated as a primitive operation that must return a ```bool```
value, not as an ```if```-statement, therefore an ```else``` is not required

#### Syntax
```
match <statement> {
    case <identifier>:<type> [if <predicate>] | <literal>[ | <literal>]* | <range> | _ => <statement>
    <next case> ...
}
```

#### Example
```
let a = 5;
match a {
    case a: bool => false,
    case a: int if a < 3 => false,
    case 6 | 7 | 8 => false,
    case 10~15 => false,
    case _ => true
}
```
Returns ```true```