## Petl REPL

To run the REPL, run Petl with no ```--file``` input.<br>
For a list of commands during usage, input ```@help```.<br>

#### Commands:
- @help - Displays all REPL commands
- @quit - Exit the REPL
- @prev - Show previous input in history
- @next - Show next input in history
- @clear - Clear all input history
- @history - Display all input history

---

## Comments

To leave a comment in Petl code, simply start it with ```#```.
Anything from the start to the end of the line will be considered as part of the comment.

Example
```
# this variable does xyz
let a = 5;
println(a) # outputting to stdout
```