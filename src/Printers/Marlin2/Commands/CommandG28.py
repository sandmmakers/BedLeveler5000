from .PositionOkCommand import PositionOkCommand
from . import Converter

class CommandG28(PositionOkCommand):
    NAME = 'G28'

    def __init__(self, *, l=False, o=False, r=None, x=False, y=False, z=False):
        self.l = l
        self.o = o
        self.r = r
        self.x = x
        self.y = y
        self.z = z

        lPart = ' L' if self.l else ''
        oPart = ' O' if self.o else ''
        rPart = '' if self.r is None else Converter.floatToStr(self.r, prefix=' R')
        xPart = ' X' if self.x else ''
        yPart = ' Y' if self.y else ''
        zPart = ' Z' if self.z else ''

        super().__init__(self.NAME + lPart + oPart + rPart + xPart + yPart + zPart)


    def _processLine(self, line):
        if line == 'Taring probe':
            return False

        return super()._processLine(line)