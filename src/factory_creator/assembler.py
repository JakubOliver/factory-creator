class Assembler:
    """
    Represents an assembler in which the recipes are crafted.
    """

    def __init__(self, multiplicator: float):
        self.multiplicator = multiplicator

class AssemblingMachine3(Assembler):
    """
    Represents tier 3 assembler.
    """

    def __init__(self):
        super().__init__(1.25)