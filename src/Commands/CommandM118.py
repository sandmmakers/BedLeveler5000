from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandM118(CommandBase):
    NAME = 'M118'
    LINE_COUNT = 2

    def __init__(self, id_, *, context=None, a1=False, e1=False, pn=None, string=None):
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

        super().__init__(id_,
                         self.NAME + a1Part + e1Part + pnPart + stringPart,
                         context)

    def parseResponse(self, lines):
        # Line 0: string
        # Line 1: ok

        self.verifyLineCount(lines)
        self.__class__.verifyOkResponseLine(lines[1])

        # Return string value, stripping the trailing carriages return, if present
        return {'string': lines[0][:-1] if lines[0].endswith('\r') else lines[0]}