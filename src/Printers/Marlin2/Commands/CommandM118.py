from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandM118(CommandBase):
    NAME = 'M118'

    def __init__(self, *, a1=False, e1=False, pn=None, string=None):
        self.a1 = a1
        self.e1 = e1
        self.pn = pn
        self.string = string

        a1Part = ' A1' if a1 else ''
        e1Part = ' E1' if e1 else ''

        if pn is None:
            pnPart = ''
        else:
            if pn < 0 or pn > 9:
                raise ValueError(f'pn must be an integer between 0 and 9 (inclusive).')
            pnPart = f' Pn{pn}'

        stringPart = '' if string is None else ' ' + string

        super().__init__(self.NAME + a1Part + e1Part + pnPart + stringPart)


    def _processLine(self, line):
        # Line 0: string
        # Line 1: ok

        if self.result is None:
            self.result = {'string': line[:-1] if line.endswith('\r') else line}
        else:
            self.verifyOkResponseLine(line)
            return True

        return False