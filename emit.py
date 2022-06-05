# Emitter object keeps track of the generated code and outputs it.
class Emitter:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.header = ""
        self.code = ""
        self.id = 0

    def emit(self, code):
        if self.code and self.code[-1] in "\n\t":
            self.code += self.id * "\t" + code
        else:
            self.code += code

    def emitLine(self, code):
        if self.code and self.code[-1] == "\n":
            self.code += self.id * "\t" + code + "\n"
        else:
            self.code += code + "\n"

    def headerLine(self, code):
        self.header += code + "\n"

    def writeFile(self):
        with open(self.fullPath, "w") as outputFile:
            outputFile.write(self.header + self.code)
