## Primitive Operations
Like any another language, Petl hosts the usual unary and binary arithmetic and boolean
operators. Usual operator precedence takes place.

---

## Arithmetic Operators
- ```+```
- ```-```
- ```*```
- ```/```
- ```%```

---

## Boolean Operators
- ```<```
- ```>```
- ```<=```
- ```>=```
- ```==```
- ```!=```
- ```not```
- ```and```
- ```or```

---

## Other
- ```++``` Used for concatenating 2 [iterable-types](./collections.md) together, preserves order.
Same precedence as ```+``` and ```-```
```
let a = [1, 2, 3];
let b = [4, 5, 6];
a ++ b
```
Returns ```[1, 2, 3, 4, 5, 6]```