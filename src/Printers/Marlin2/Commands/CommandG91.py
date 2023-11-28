from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandG91(CommandBase):
    NAME = 'G91'

    def __init__(self):
        super().__init__(self.NAME)

    def _processLine(self, line):
        # Line 0: ok

        self.verifyOkResponseLine(line)
        return True