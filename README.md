# Skeedge#

Skeedge# (pronounced *Skeedge Sharp*) is a compiled programming language written in Python.
It has fairly simple syntax and is similar to Basic/Visual Basic but with some C/Java elements.
Skeedge# transpiles to Python.

Here's some example code:
```
Module {
    # Single-line comments use the hash mark.
    ~ Multi-line comments use
      the tilde symbol. ~

    PrintLn("Hello, world!");
    Var myVar = 10; # No type hinting
    InputNum myInputVar; # Get input from stdin

    # While loops
    While myVar > 0 {
        PrintLn(myVar);
        Var myVar = myVar - 1;
    };

    # If statements
    If myInputVar < 2 {
        PrintLn("That's less than two!");
    };

};
```