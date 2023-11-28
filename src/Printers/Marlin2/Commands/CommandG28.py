from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandG28(CommandBase):
    NAME = 'G28'
    IGNORE_LINES = ['Taring probe'] # Observed with a Neptune 3 Pro

    def __init__(self, *, l=False, o=False, r=False, x=False, y=False, z=False):
        self.l = l
        self.o = o
        self.r = r
        self.x = x
        self.y = y
        self.z = z

        lPart = ' L' if self.l else ''
        oPart = ' O' if self.o else ''
        rPart = ' R' if self.r else ''
        xPart = ' X' if self.x else ''
        yPart = ' Y' if self.y else ''
        zPart = ' Z' if self.z else ''

        super().__init__(self.NAME + lPart + oPart + rPart + xPart + yPart + zPart)

    def _processLine(self, line):
        # Line 0: position
        # Line 1: ok

        # Check for ignore lines
        if line in self.IGNORE_LINES:
            return False

        if self.result is None:
            self.result = self.parsePositionResponseLine(line)
        else:
            self.verifyOkResponseLine(line)
            return True

        return False