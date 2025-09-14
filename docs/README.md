## A Tour of Petl

---

Petl is a (toy) strongly, statically-typed, interpreted, general-purpose language 
focused on table-based data manipulation. It is so focused in fact, that tables 
and schemas are each their own first-class type in Petl. Likewise, queries for Petl's 
builtin table functions use Petl Query Langauge (PQL) for direct manipulation 
of these ```table```-types. This allows Petl to simultaneously act as a pseudo 
hybrid of something akin to Python for scripting and SQL for data manipulation. 
In turn, Petl finds its niche as a lightweight means of processing 
small sets of data, or for prototyping larger dataset processing via subsets.

---

###### Note: Please keep in mind that this is a project langauge and therefore the realistic functionality is somewhat minimal. This is as much for fun as it is academic.

---

- Basics
  - [REPL and Comments](./petl/basics/repl_comments.md)
  - [Variables and Primitve Types](./petl/basics/variables_and_prims.md)
  - [Arithmetic and Boolean Operations](./petl/basics/arith_bool_ops.md)
  - [Flow Control](./petl/basics/flow_control.md)
  - [Collections](./petl/basics/collections.md)
  - [Lambdas](./petl/basics/lambdas.md)
- Advanced
  - [Pattern Matching](./petl/advanced/pattern_matching.md)
  - [Tables and Schemas](./petl/advanced/tables_schemas.md)
  - [PQL](./petl/advanced/queries.md)
  - [Other](./petl/advanced/other.md)
    * ```union```-types
    * Ranges
    * Type-aliasing
- [Builtin Functions](./petl/builtin/builtin.md)

---