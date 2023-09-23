from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandM114(CommandBase):
    NAME = 'M114'
    LINE_COUNT = 2

    def __init__(self, id_, *, context=None, d=None, e=None, r=None):
        self.d = d
        self.e = e
        self.r = r

        dPart = ' D' if self.d else ''
        ePart = ' E' if self.e else ''
        rPart = ' R' if self.r else ''

        super().__init__(id_,
                         self.NAME + dPart + ePart + rPart,
                         context)

    def parseResponse(self, lines):
        # Line 0: position
        # Line 1: ok

        self.verifyLineCount(lines)
        self.__class__.verifyOkResponseLine(lines[1])

        return self.__class__.parsePositionResponseLine(lines[0])