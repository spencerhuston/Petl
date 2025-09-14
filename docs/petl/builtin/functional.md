## Functional builtins

---

```map(c: iterable, f: (any) -> any) -> list[any]```
Returns a list where function ```f``` is applied to each element of list ```l```
Will always return a ```list``` with elements of the return-type of ```f```

---

```filter(c: iterable, f: (any) -> bool) -> list[any]```<br>
Returns a list where each element in ```iterable``` satisfies a boolean condition 
in ```func```

---

```foldl(l: list[any], i: any, f: (any, any) -> any) -> any```<br>
Left-associative linear fold on list ```l```, starting with initial value ```i```, 
and according to the function ```f```

---

```foldr(l: list[any], i: any, f: (any, any) -> any) -> any```<br>
Right-associative linear fold on list ```l```, starting with initial value ```i```,
and according to the function ```f```