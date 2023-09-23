from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandG28(CommandBase):
    NAME = 'G28'
    LINE_COUNT = 2

    def __init__(self, id_, *, context=None, l=False, o=False, r=False, x=False, y=False, z=False):
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

        super().__init__(id_,
                         self.NAME + lPart + oPart + rPart + xPart + yPart + zPart,
                         context)

    def parseResponse(self, lines):
        # Line 0: position
        # Line 1: ok

        self.verifyLineCount(lines)
        self.__class__.verifyOkResponseLine(lines[1])

        return self.__class__.parsePositionResponseLine(lines[0])