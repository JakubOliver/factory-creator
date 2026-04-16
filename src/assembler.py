class Assembler:
    def __init__(self, multiplicator: float):
        self.multiplicator = multiplicator

class AssemblingMachine3(Assembler):
    def __init__(self):
        super().__init__(1.25)

        print(self.multiplicator)