from .CommandBase import CommandBase
from . import Converter

class CommandM420(CommandBase):
    NAME = 'M420'

    def __init__(self, *, c=False, l=None, s=False, t=None, v=False, z=None):
        self.c = c
        self.l = l
        self.s = s
        self.t = t
        self.v = v
        self.z = z

        cPart = ' C' if self.c else ''
        lPart = f' L{self.l}' if self.l is not None else ''
        sPart = ' S' if self.s else ''
        if self.t is None:
            tPart = ''
        else:
            if t not in [0, 1, 4]:
                raise ValueError(f't must be either 0, 1, or 4.')
            tPart = f' T{self.t}'
        vPart = ' V' if self.v else ''
        zPart = '' if self.z is None else Converter.floatToStr(self.z, prefix=' Z')

        super().__init__(self.NAME + cPart + lPart + sPart + tPart + vPart + zPart)

    def _processLine(self, line):
        # Line 0: ???
        # ...
        # Line ?: ok

        if self.isMetadata(line) or \
           (self.isAutoReport(line) and self.result is None):
            return False

        if self.result is None:
            self.result = {'response': []}

        if line.startswith('ok'):
            self.verifyOkResponseLine(line)
            return True
        else:
            self.result['response'].append(line)

        return False