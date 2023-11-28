from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandM114(CommandBase):
    NAME = 'M114'

    def __init__(self, *, d=None, e=None, r=None):
        self.d = d
        self.e = e
        self.r = r

        dPart = ' D' if self.d else ''
        ePart = ' E' if self.e else ''
        rPart = ' R' if self.r else ''

        super().__init__(self.NAME + dPart + ePart + rPart)

    def _processLine(self, line):
        # Line 0: position
        # Line 1: ok

        if self.result is None:
            self.result = self.parsePositionResponseLine(line)
        else:
            self.verifyOkResponseLine(line)
            return True

        return False