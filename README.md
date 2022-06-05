# Cobalt: A small but functional programming language

Cobalt is a compiled programming language written in Python.
It has fairly simple syntax and is similar to Basic/Visual Basic but with some C/Java elements.
Cobalt transpiles to Python code.

Here's some example code:
```
# All code must be contained in a Module.
Module {
    # Single-line comments use the hash mark.
    ~ Multi-line comments use
      the tilde symbol. ~

    PrintLn("Hello, world!");
    Var myVar = 10; # No type hinting

    # While loops
    While myVar > 0 {
      PrintLn(myVar); # Indentation isn't needed anywhere, but it looks nicer.
      Var myVar = myVar - 1;
    };

    If myVar == 4 {
      Print(myVar); # 'Print' doesn't output a newline, 'PrintLn' does
      PrintLn(" is equal to four!");
    };
};
```