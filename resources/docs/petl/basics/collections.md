## Collections (Iterables)

---

### Lists
```List```-types in Petl are immutable arrays, and have a slew of 
[builtin functions](../builtin/list.md) available for use.

Declaration syntax<br>
```[x1, x2, ..., xn]```

Index access<br>
```<list reference>(<integer value>)```

Type-hint<br>
```list[<type>]```

#### Example
```
let a: list[int] = [0, 1, 2, 3];
let b = a(1); # equals 1
let c: list[list[char]] = [
    ['a', 'b'],
    ['c', 'd']
]
let d: char = c(1)(1) # equals 'd'
```

---

### Tuples
```tuple```-types are Petl's immutable polymorphic collections, with support for unpacking
for variable declaration. **Note** that literal ```tuple``` values _cannot_ be declared empty, 
like ```()```, there must be at least 1 value present.

Declaration syntax<br>
```(x1, x2, ..., xn)```

Index access<br>
```<tuple reference>(<integer value>)```

Type-hint<br>
```tuple[<type>]```

#### Example
```
let a: tuple[char, int, bool] = ('a', 1, false);
let b: int = a(1); # equals 1
let c: list[tuple[char, int]] = [
    ('a', 0),
    ('b', 1)
]
let d: int = c(1)(1) # equals 1
```

#### Variable unpacking
```
let t = (0, 'a', true);
let i: int, a: char, b: bool = t
```

---

### Dictionaries
```Dict```-types are immutable, monomorphic, key-based collections.

Declaration syntax<br>
```[k1: v1, k2: v2, ..., kn: vn]```

Index access<br>
```<dict reference>(<key value>)```

Type-hint<br>
```dict[<key type>: <value type>]```

#### Example
```
let a: dict[char: int] = ['a': 1, 'b': 2];
let b: int = a('b'); # equals 2
let c: dict[int: tuple[char, int]] = [
    0: ('a', 0),
    1: ('b', 1)
]
let d: int = c(0)(1) # equals 0
```