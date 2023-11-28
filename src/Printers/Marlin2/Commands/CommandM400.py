from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandM400(CommandBase):
    NAME = 'M400'

    def __init__(self):
        # Build request
        super().__init__(self.NAME)

    def _processLine(self, line):
        # Line 0: ok

        self.verifyOkResponseLine(line)
        return True