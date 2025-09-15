## Other

---

Petl supports a few other nice-to-have features.

---

### Ranges
Syntactic sugar for in-place ```list[int]``` construction, done via the ```~``` operator
between 2 integer literal values. **Note** that both bounds are inclusive to the range.
Steps or any type other than ```int``` are currently not supported.

#### Example
```
let a = 0~5; # Same as [0, 1, 2, 3, 4, 5];
for i in 5~9 {
    print(i)
}
```
Prints ```56789```

---

### Union-types
Petl suppors ```union```-types, allowing for variables to act polymorphic.

#### Type-hint
```union[<type>[, <type>]*]```

#### Example
```
let f = |x: int| -> union[int, char] {
    if (x > 5) { x } else { 'b' }
};
let u: union[int, char] = f(2)
```
Result ```'b'```

---

### Type-aliasing
More syntactic sugar, this time for condensing down long type-hints.

#### Syntax
```
alias <identifier> = <type>
```

#### Example
```
alias long_type = list[tuple[dict[int: char], bool]];
let a: long_type = [
    (['a': 1, 'b': 2], false),
    (['c': 3, 'd': 4], true)
]
```