import enum
import sys


# Token contains the original text and the type of token.
class Token:
    """Token class for parsing."""

    def __init__(self, tokenText, tokenKind):
        self.text = (
            tokenText  # The token"s actual text. Used for identifiers, strings, and numbers.
        )
        self.kind = tokenKind  # The TokenType that this token is classified as.

    @staticmethod
    def checkIfKeyword(tokenText):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == tokenText and kind.value >= 100 and kind.value < 200:
                return kind
        return None


# TokenType is our enum for all the types of tokens.
class TokenType(enum.Enum):
    """List of token types."""

    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    SEMI = 4
    LBRACE = 5
    RBRACE = 6
    LPAREN = 7
    RPAREN = 8
    COLON = 9
    COMMA = 10

    # Keywords.
    Module = 100
    Print = 101
    PrintLn = 102
    Var = 103
    If = 104
    Else = 105
    ElseIf = 106
    While = 107
    Func = 108
    Return = 109

    # Operators.
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211


KEYWORDS = [tt for tt in TokenType]


class Lexer:
    """Lexer class to easily generate tokens."""

    def __init__(self, input):
        self.source = (
            input + "\n"
        )  # Source code to lex as a string. Append a newline to simplify lexing/parsing the last token/statement.
        self.curChar = ""  # Current character in the string.
        self.curPos = -1  # Current position in the string.
        self.nextChar()

    # Process the next character.
    def nextChar(self):
        """Process the next character."""
        self.curPos += 1
        if self.curPos >= len(self.source):
            self.curChar = "\0"  # EOF
        else:
            self.curChar = self.source[self.curPos]

    # Return the lookahead character.
    def peek(self):
        """Return the lookahead character."""
        if self.curPos + 1 >= len(self.source):
            return "\0"
        return self.source[self.curPos + 1]

    # Invalid token found, print error message and exit.
    def abort(self, message):
        """Invalid token found, print error message and exit."""
        sys.exit("Lexing error. " + message)

    # Skip whitespace except newlines, which we will use to indicate the end of a statement.
    def skipWhitespace(self):
        """Skip whitespace except newlines, which we will use to indicate the end of a statement."""
        while self.curChar == " " or self.curChar == "\t" or self.curChar == "\r":
            self.nextChar()

    # Skip comments in the code.
    def skipComment(self):
        """Skip comments in the code."""
        if self.curChar == "~":
            self.nextChar()
            while self.curChar != "~":
                self.nextChar()
            self.nextChar()
        elif self.curChar == "#":
            while self.curChar != "\n":
                self.nextChar()

    # Return the next token.
    def getToken(self):
        """Return the next token."""
        # Check the first character of this token to see if we can decide what it is.
        # If it is a multiple character operator (e.g., !=), number, identifier, or keyword then we will process the rest.

        # Skip all whitespace characters.
        self.skipWhitespace()
        self.skipComment()
        token = None

        if self.curChar == "+":
            token = Token(self.curChar, TokenType.PLUS)
        elif self.curChar == "-":
            token = Token(self.curChar, TokenType.MINUS)
        elif self.curChar == "*":
            token = Token(self.curChar, TokenType.ASTERISK)
        elif self.curChar == "/":
            token = Token(self.curChar, TokenType.SLASH)
        elif self.curChar == ";":
            token = Token(self.curChar, TokenType.SEMI)
        elif self.curChar == "\n":
            token = Token(self.curChar, TokenType.NEWLINE)
        elif self.curChar == "\0":
            token = Token("", TokenType.EOF)
        elif self.curChar == "{":
            token = Token(self.curChar, TokenType.LBRACE)
        elif self.curChar == "}":
            token = Token(self.curChar, TokenType.RBRACE)
        elif self.curChar == "(":
            token = Token(self.curChar, TokenType.LPAREN)
        elif self.curChar == ")":
            token = Token(self.curChar, TokenType.RPAREN)
        elif self.curChar == ",":
            token = Token(self.curChar, TokenType.COMMA)
        elif self.curChar == "=":
            # Check whether this token is = or ==
            if self.peek() == "=":
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.EQEQ)
            else:
                token = Token(self.curChar, TokenType.EQ)
        elif self.curChar == ">":
            # Check whether this is token is > or >=
            if self.peek() == "=":
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.GTEQ)
            else:
                token = Token(self.curChar, TokenType.GT)
        elif self.curChar == "<":
            # Check whether this is token is < or <=
            if self.peek() == "=":
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.LTEQ)
            else:
                token = Token(self.curChar, TokenType.LT)
        elif self.curChar == "!":
            if self.peek() == "=":
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())
        elif self.curChar == '"':
            # Get characters between quotations.
            self.nextChar()
            startPos = self.curPos

            while self.curChar != '"':
                self.nextChar()

            tokText = self.source[startPos : self.curPos]  # Get the substring.
            token = Token(tokText, TokenType.STRING)
        elif self.curChar.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            startPos = self.curPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == ".":  # Decimal!
                self.nextChar()

                # Must have at least one digit after decimal.
                if not self.peek().isdigit():
                    # Error!
                    self.abort(f"Illegal character in number: {self.curChar}")
                while self.peek().isdigit():
                    self.nextChar()

            tokText = self.source[startPos : self.curPos + 1]  # Get the substring.
            token = Token(tokText, TokenType.NUMBER)
        elif self.curChar.isalpha():
            # Leading character is a letter, so this must be an identifier or a keyword.
            # Get all consecutive alpha numeric characters.
            startPos = self.curPos
            while self.peek().isalnum():
                self.nextChar()

            # Check if the token is in the list of keywords.
            tokText = self.source[startPos : self.curPos + 1]  # Get the substring.
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None:  # Identifier
                token = Token(tokText, TokenType.IDENT)
            else:  # Keyword
                token = Token(tokText, keyword)
        else:
            # Unknown token!
            self.abort("Unknown token: {}".format(self.curChar))

        self.nextChar()
        return token
