from lex import *
from emit import *
from parse import *
import sys
import argparse

if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Skeedge# transpiler to C written in Python")
    ap.add_argument("infile", type=str, help="Skeedge# source file")
    ap.add_argument("outfile",
                    type=str,
                    help="Filename to output to (default is input filename)",
                    default=None)

    args = ap.parse_args()

    with open(args.infile) as infile:
        code = infile.read()

    # Initialize the lexer, emitter, and parser.
    lexer = Lexer(code)

    outfile = args.outfile

    if not outfile:
        emitter = Emitter(f"{infile[:-3]}.c")
    else:
        emitter = Emitter(f"{outfile}.c") if outfile[-2:] != ".c" else Emitter(
            f"{outfile}")

    parser = Parser(lexer, emitter)

    parser.program()  # Start the parser.
    emitter.writeFile()  # Write the output to file.
    print("Compiling completed.")