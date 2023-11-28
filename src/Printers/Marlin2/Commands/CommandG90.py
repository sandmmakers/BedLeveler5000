from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandG90(CommandBase):
    NAME = 'G90'

    def __init__(self):
        super().__init__(self.NAME)

    def _processLine(self, line):
        # Line 0: ok

        self.verifyOkResponseLine(line)
        return True