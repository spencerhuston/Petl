## List-type builtins

---

```insert(l: list[any], v: any, i: int) -> list[any]```<br>
Returns a new copy of list ```l``` with ```v``` inserted at index ```i```

---

```remove(l: list[any], i: int) -> list[any]```<br>
Returns a new copy of list ```l``` with the element at index ```i``` removed

---

```replace(l: list[any], i: int, v: any) -> list[any]```<br>
Returns a new copy of list ```l``` with the element at index ```i``` replace with ```v```

---

```front(l: list[any]) -> any```<br>
Returns the first element of ```l```

---

```back(l: list[any]) -> any```<br>
Returns the last element of ```l```

---

```head(l: list[any]) -> any```<br>
Returns all but the last element of ```l```

---

```tail(l: list[any]) -> any```<br>
Returns all but the first element of ```l```

---

```slice(l: list[any], start: int, end: int) -> list[any]```<br>
Return slice of ```l``` from [```start```, ```end```)

---

```contains(l: list[any], v: any) -> bool```<br>
Return ```true``` if ```v``` in ```l```, ```false``` otherwise
Return slice of ```l``` from [```start```, ```end```)

---

```find(l: list[any], v: any) -> bool```<br>
Return the index of ```v``` in ```l```, ```-1``` otherwise

---

```fill(c: int, v: any) -> bool```<br>
Creates a new list of size ```c```, each element a copy of value ```v```

---

```reverse(l: list[any]) -> list[any]```<br>
Reverses the given list ```l```

---

```set(l1: list[any], l2: list[any]) -> list[any]```<br>
Returns a new list comprised of the combined set of ```l1``` and ```l2```,
all duplicates removed.

---

```intersect(l1: list[any], l2: list[any]) -> list[any]```<br>
Returns a new list comprised of the intersection of ```l1``` and ```l2```