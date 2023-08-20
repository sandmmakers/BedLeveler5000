from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandM105(CommandBase):
    NAME = 'M105'
    LINE_COUNT = 1

    def __init__(self, id_, *, context=None, r=False, t=None):
        super().__init__(id_, context)

        self.r = r
        self.t = t

        rPart = ' R' if self.r else ''
        tPart = f' T{self.t}' if self.t is not None else ''

        self.request = self.NAME + rPart + tPart

    def parseResponse(self, lines):
        # Line 0: 'ok T:<FLOAT> /<FLOAT> B:<FLOAT> /<FLOAT> @:<FLOAT> B@:<FLOAT>
        #          |  |         |        |         |        |         +----------- Bed power
        #          |  |         |        |         |        +--------------------- Tool power
        #          |  |         |        |         +------------------------------ Bed temp (desired)
        #          |  |         |        +---------------------------------------- Bed temp (actual)
        #          |  |         +------------------------------------------------- Tool temp (desired)
        #          |  +----------------------------------------------------------- Tool temp (actual)
        #          +-------------------------------------------------------------- ok

        self.verifyLineCount(lines)

        tokens = CommandBase.tokenize(lines[0], 11, replace=':')

        if tokens[0] != 'ok' or \
           tokens[1] != 'T' or \
           not tokens[3].startswith('/') or \
           tokens[4] != 'B' or \
           not tokens[6].startswith('/') or \
           tokens[7] != '@' or \
           tokens[9] != 'B@':
            raise GCodeError(f'Unable to parse response: [{lines[0]}].')

        try:
            return {'toolActual':  float(tokens[2]),
                    'toolDesired': float(tokens[3][1:]),
                    'bedActual':   float(tokens[5]),
                    'bedDesired':  float(tokens[6][1:]),
                    'toolPower':   float(tokens[8]),
                    'bedPower':    float(tokens[10])}

        except ValueError:
            raise GCodeError(f'Incorrect numeric data type found in response: [{lines[0]}].')