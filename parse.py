import sys
from lex import *


# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()  # All variables we have declared so far.
        self.functions = set()  # All functions declared so far.
        self.in_func = False  # True if we are in a function, false otherwise.

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()  # Call this twice to initialize current and peek.

    # Return true if the current token matches.
    def checkToken(self, kind):
        """Return true if the current token matches."""
        return kind == self.curToken.kind

    # Return true if the next token matches.
    def checkPeek(self, kind):
        """Return true if the next token matches."""
        return kind == self.peekToken.kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind):
        """Try to match the current token. If not, error. Advances the current token."""
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " +
                       self.curToken.kind.name)
        self.nextToken()

    # Advances the current token.
    def nextToken(self):
        """Advances the current token."""
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        # No need to worry about passing the EOF, lexer handles that.

    def abort(self, message):
        """Abort the program."""
        sys.exit("Error: " + message)

    # Production rules.

    # program ::= Module {statement};
    def program(self):
        """Program node for the AST."""

        self.emitter.headerLine("import pyinputplus\n")

        # Since some newlines are required in our grammar, need to skip the excess.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        self.module()

    # Module ::= {statement}
    def module(self):
        """Module node for the AST."""
        self.emitter.emitLine("if __name__ == \"__main__\":")
        self.emitter.id += 1
        self.match(TokenType.Module)
        self.match(TokenType.LBRACE)

        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # Parse all the statements in the program.
        while not self.checkToken(TokenType.RBRACE):
            self.statement()

        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
        self.match(TokenType.RBRACE)
        self.match(TokenType.SEMI)

    # One of the following statements...
    def statement(self):
        """Statement node for the AST."""
        # Check the first token to see what kind of statement this is.

        # Print (no newline) ::= "Print" "(" (expression | string) ")"
        if self.checkToken(TokenType.Print):
            self.nextToken()
            self.match(TokenType.LPAREN)
            if self.checkToken(TokenType.STRING):
                self.emitter.emitLine("print(\"" + self.curToken.text +
                                      "\", end='')")
                self.nextToken()
            else:
                self.emitter.emit("print(")
                self.expression()
                self.emitter.emitLine(", end='')")

            self.match(TokenType.RPAREN)

        # Print (with newline) ::= "PrintLn" "(" (expression | string) ")"
        if self.checkToken(TokenType.PrintLn):
            self.nextToken()
            self.match(TokenType.LPAREN)
            if self.checkToken(TokenType.STRING):
                self.emitter.emitLine("print(\"" + self.curToken.text + "\")")
                self.nextToken()
            else:
                self.emitter.emit("print(")
                self.expression()
                self.emitter.emitLine(")")

            self.match(TokenType.RPAREN)

        # If-statement ::= "If" comparison "{" {statement} "}"
        elif self.checkToken(TokenType.If):
            self.nextToken()
            self.emitter.emit("if ")
            self.comparison()

            self.match(TokenType.LBRACE)
            self.nl()
            self.emitter.emitLine(":")
            self.emitter.id += 1

            # Zero or more statements in the body.
            while not self.checkToken(TokenType.RBRACE):
                self.statement()

            self.match(TokenType.RBRACE)
            self.emitter.id -= 1

        # While loop ::= "While" comparison "{" {statement} "}"
        elif self.checkToken(TokenType.While):
            self.nextToken()
            self.emitter.emit("while ")
            self.comparison()

            self.match(TokenType.LBRACE)
            self.nl()
            self.emitter.emitLine(":")
            self.emitter.id += 1

            # Zero or more statements in the loop body.
            while not self.checkToken(TokenType.RBRACE):
                self.statement()

            self.match(TokenType.RBRACE)
            self.emitter.id -= 1

        # Function definition ::= "Func" ident "{" {statement} "}"
        elif self.checkToken(TokenType.Func):
            self.nextToken()
            if self.curToken.text in self.symbols:
                self.abort(
                    f"Cannot name function '{self.curToken.text}'- name already taken"
                )

            self.emitter.emitLine("")
            self.emitter.emitLine(f"def {self.curToken.text}():")
            self.in_func = True

            # Add the function name to the list of functions.
            self.functions.add(self.curToken.text)

            self.match(TokenType.IDENT)

            self.emitter.id += 1

            self.match(TokenType.LBRACE)
            self.nl()

            while not self.checkToken(TokenType.RBRACE):
                self.statement()

            self.match(TokenType.RBRACE)
            self.emitter.id -= 1
            self.emitter.emitLine("")
            self.in_func = False

        # Variable definition ::= variable "=" expression
        elif self.checkToken(TokenType.Var):
            self.nextToken()
            self.symbols.add(self.curToken.text)
            self.emitter.emit(f"{self.curToken.text} = ")
            self.match(TokenType.IDENT)
            self.expression()
            self.emitter.emitLine("")

        # Input ::= "Input" ident
        elif self.checkToken(TokenType.Input):
            self.nextToken()

            self.symbols.add(self.curToken.text.strip("$"))

            self.emitter.emitLine(self.curToken.text + " = input()")
            self.match(TokenType.VARIABLE)

        # InputNum ::= "InputNum" ident
        elif self.checkToken(TokenType.InputNum):
            self.nextToken()

            self.symbols.add(self.curToken.text.strip("$"))

            self.emitter.emitLine(self.curToken.text +
                                  " = pyinputplus.inputNum()")
            self.match(TokenType.IDENT)

        # Abort ::= "Abort" "(" STRING ")"
        elif self.checkToken(TokenType.Abort):
            self.nextToken()
            self.match(TokenType.LPAREN)
            msg = self.curToken.text
            self.match(TokenType.STRING)
            self.emitter.emitLine("raise Exception(\"" + msg + "\")")
            self.match(TokenType.RPAREN)

        # Function call ::= ident "()"
        elif self.checkToken(TokenType.IDENT):
            name = self.curToken.text
            self.nextToken()
            if self.checkToken(TokenType.LPAREN):
                self.nextToken()
                if self.checkToken(TokenType.RPAREN):
                    # This is a function call. Check if the function exists.
                    if name not in self.functions:
                        self.abort(
                            f"Referencing function before assignment: {name}")
                    self.emitter.emitLine(f"{name}()")
                    self.nextToken()
                else:
                    self.abort(f"Expected ')', got {self.curToken.text}")

        # Return statement: must be inside a function ::= "Return" ident | expression | string
        elif self.checkToken(TokenType.Return):
            self.nextToken()
            if self.in_func:
                if self.checkToken(TokenType.IDENT):
                    if self.curToken.text not in self.symbols:
                        self.abort(
                            f"Referencing variable before assignment: {self.curToken.text}"
                        )
                    self.emitter.emitLine(f"return {self.curToken.text}")
                    self.nextToken()
                elif self.checkToken(TokenType.STRING):
                    self.emitter.emitLine(f"return {self.curToken.text}")
                    self.nextToken()
                else:
                    # Expect expression
                    self.nextToken()
                    self.expression()
            else:
                self.abort("'Return' outside of function")

        # This is not a valid statement. Error!
        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" +
                       self.curToken.kind.name + ")")

        # Semicolon and newline.
        self.semi_nl()

    # Return true if the current token is a comparison operator.
    def isComparisonOperator(self):
        """Check if the current token is a comparison operator."""
        return self.checkToken(TokenType.GT) or self.checkToken(
            TokenType.GTEQ) or self.checkToken(
                TokenType.LT) or self.checkToken(
                    TokenType.LTEQ) or self.checkToken(
                        TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        """Comparison node for the AST."""
        self.expression()
        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
        # Can have 0 or more comparison operator and expressions.
        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        """Expression node for the AST."""
        self.term()
        # Can have 0 or more +/- and expressions.
        while self.checkToken(TokenType.PLUS) or self.checkToken(
                TokenType.MINUS):
            self.emitter.emit(" " + self.curToken.text + " ")
            self.nextToken()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        """Term node for the AST."""
        self.unary()
        # Can have 0 or more *// and expressions.
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(
                TokenType.SLASH):
            self.emitter.emit(" " + self.curToken.text + " ")
            self.nextToken()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        """Unary node for the AST."""
        # Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(" " + self.curToken.text + " ")
            self.nextToken()
        self.primary()

    # primary ::= number | ident
    def primary(self):
        """Primary node for the AST."""
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.VARIABLE):
            # Ensure the variable already exists.
            if self.curToken.text.strip("$") not in self.symbols:
                self.abort("Referencing variable before assignment: " +
                           self.curToken.text)

            self.emitter.emit(self.curToken.text.strip("$"))
            self.nextToken()
        else:
            # Error!
            self.abort("Unexpected token at " + self.curToken.text)

    # nl ::= "\n"+
    def nl(self):
        """Match one or more newlines."""
        # Require at least one newline.
        self.match(TokenType.NEWLINE)
        # But we will allow extra newlines too, of course.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    def semi_nl(self):
        """Match one semicolon and optional newlines."""
        # Require a semicolon..
        self.match(TokenType.SEMI)

        # Skip all newlines.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
