from .GCodeError import GCodeError
from .CommandBase import CommandBase
from . import Converter

class CommandG30(CommandBase):
    NAME = 'G30'

    def __init__(self, *, c=None, e=None, x=None, y=None):
        self.c = c
        self.e = e
        self.x = x
        self.y = y

        cPart = ' C1' if self.c else ' C0'
        ePart = ' E1' if self.e else ' E0'
        xPart = '' if self.x is None else Converter.floatToStr(self.x, prefix=' X')
        yPart = '' if self.y is None else Converter.floatToStr(self.y, prefix=' Y')

        super().__init__(self.NAME + cPart + ePart + xPart + yPart)

    def _processLine(self, line):
        # Line 0: bed
        # Line 1: position
        # Line 2: ok

        if self.result is None:
            self.result = {'bed': self.parseBedResponseLine(line)}
        elif 'position' not in self.result:
            self.result['position'] = self.parsePositionResponseLine(line)
        else:
            self.verifyOkResponseLine(line)
            return True

        return False