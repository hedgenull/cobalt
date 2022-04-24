import sys
from lex import *


# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()  # All variables we have declared so far.
        self.labelsDeclared = set()  # Keep track of all labels declared
        self.labelsGotoed = set(
        )  # All labels goto'ed, so we know if they exist or not.

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
        self.emitter.headerLine("#include <stdio.h>\n")

        # Since some newlines are required in our grammar, need to skip the excess.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        self.module()

    # Module ::= {statement}
    def module(self):
        """Module node for the AST."""
        self.emitter.headerLine("int main (void) {")
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

        # Check that each label referenced in a GOTO is declared.
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO to undeclared label: " + label)

        # Wrap things up.
        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")

    # One of the following statements...
    def statement(self):
        """Statement node for the AST."""
        # Check the first token to see what kind of statement this is.

        # "PrintLn" "(" (expression | string) ")"
        if self.checkToken(TokenType.PrintLn):
            self.nextToken()
            self.match(TokenType.LPAREN)

            if self.checkToken(TokenType.STRING):
                # Simple string, so print it.
                self.emitter.emitLine("printf(\"" + self.curToken.text +
                                      "\\n\");")
                self.nextToken()

            else:
                # Expect an expression and print the result as a float.
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emitLine("));")
            self.match(TokenType.RPAREN)

        # "If" comparison "{" {statement} "}"
        elif self.checkToken(TokenType.If):
            self.nextToken()
            self.emitter.emit("if (")
            self.comparison()

            self.match(TokenType.LBRACE)
            self.nl()
            self.emitter.emitLine(") {")

            # Zero or more statements in the body.
            while not self.checkToken(TokenType.RBRACE):
                self.statement()

            self.match(TokenType.RBRACE)
            self.emitter.emitLine("}")

        # "While" comparison "{" {statement} "}"
        elif self.checkToken(TokenType.While):
            self.nextToken()
            self.emitter.emit("while (")
            self.comparison()

            self.match(TokenType.LBRACE)
            self.nl()
            self.emitter.emitLine(") {")

            # Zero or more statements in the loop body.
            while not self.checkToken(TokenType.RBRACE):
                self.statement()

            self.match(TokenType.RBRACE)
            self.emitter.emitLine("}")

        # "Label" ident
        elif self.checkToken(TokenType.Label):
            self.nextToken()

            # Make sure this label doesn't already exist.
            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)

            self.emitter.emitLine(self.curToken.text + ":")
            self.match(TokenType.IDENT)

        # "GoTo" ident
        elif self.checkToken(TokenType.GoTo):
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            self.emitter.emitLine("goto " + self.curToken.text + ";")
            self.match(TokenType.IDENT)

        # "Var" ident "=" expression
        elif self.checkToken(TokenType.Var):
            self.nextToken()

            #  Check if ident exists in symbol table. If not, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            self.emitter.emit(self.curToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)

            self.expression()
            self.emitter.emitLine(";")

        # "Input" ident
        elif self.checkToken(TokenType.InputNum):
            self.nextToken()

            # If variable doesn't already exist, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            # Emit scanf but also validate the input. If invalid, set the variable to 0 and clear the input.
            self.emitter.emitLine("if (0 == scanf(\"%" + "f\", &" +
                                  self.curToken.text + ")) {")
            self.emitter.emitLine(self.curToken.text + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emitLine("*s\");")
            self.emitter.emitLine("}")
            self.match(TokenType.IDENT)

        # "Abort" "(" STRING ")"
        elif self.checkToken(TokenType.Abort):
            self.nextToken()
            self.match(TokenType.LPAREN)
            msg = self.curToken.text
            self.match(TokenType.STRING)
            self.emitter.emitLine("printf(\"" + msg + "\");\nreturn 1;")
            self.match(TokenType.RPAREN)

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
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        """Term node for the AST."""
        self.unary()
        # Can have 0 or more *// and expressions.
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(
                TokenType.SLASH):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        """Unary node for the AST."""
        # Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        self.primary()

    # primary ::= number | ident
    def primary(self):
        """Primary node for the AST."""
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Ensure the variable already exists.
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " +
                           self.curToken.text)

            self.emitter.emit(self.curToken.text)
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
        # Require a semicolon and at least one newline.
        self.match(TokenType.SEMI)

        # But we will allow extra newlines too, of course.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
