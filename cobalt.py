import argparse

from emit import *
from lex import *
from parse import *

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Cobalt transpiler to Python")
    ap.add_argument("infile", type=str, help="Cobalt source file")
    ap.add_argument("-o", help="Python output file", default=None)

    args = ap.parse_args()

    with open(args.infile) as infile:
        code = infile.read()

    # Initialize the lexer, emitter, and parser.
    lexer = Lexer(code)

    outfile = args.o

    if not outfile:
        emitter = Emitter(f"{args.infile[:-3]}.py")
    else:
        emitter = Emitter(f"{outfile}.py") if outfile[-3:] != ".py" else Emitter(f"{outfile}")

    parser = Parser(lexer, emitter)

    parser.program()  # Start the parser.
    emitter.writeFile()  # Write the output to file.
    print("Transpiling completed.")
