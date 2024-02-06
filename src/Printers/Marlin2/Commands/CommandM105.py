from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandM105(CommandBase):
    NAME = 'M105'

    def __init__(self, *, r=False, t=None):
        self.r = r
        self.t = t

        rPart = ' R' if self.r else ''
        tPart = f' T{self.t}' if self.t is not None else ''

        super().__init__(self.NAME + rPart + tPart)

    def _processLine(self, line):
        # Line 0: 'ok T:<FLOAT> /<FLOAT> B:<FLOAT> /<FLOAT> @:<FLOAT> B@:<FLOAT>'
        #          |  |         |        |         |        |         +----------- Bed power
        #          |  |         |        |         |        +--------------------- Tool power
        #          |  |         |        |         +------------------------------ Bed temp (desired)
        #          |  |         |        +---------------------------------------- Bed temp (actual)
        #          |  |         +------------------------------------------------- Tool temp (desired)
        #          |  +----------------------------------------------------------- Tool temp (actual)
        #          +-------------------------------------------------------------- ok

        if self.isMetadata(line) or self.isAutoReport(line):
            return False

        bedPower = None
        bedTempDesired = None
        bedTempActual = None
        toolPower = None
        toolTempDesired = None
        toolTempActual = None
        tokens = line.replace(':', ' ').split()

        if tokens[0] != 'ok':
            raise GCodeError(f'Unable to parse response: [{line}].')

        try:
            index = 1
            while index < len(tokens):
                if tokens[index].startswith('T'):
                    isCurrent = toolTempActual is None and (tokens[index] in ['T', 'T0'])
                    if isCurrent:
                        toolTempActual = float(tokens[index+1])
                    index += 2

                    if tokens[index].startswith('/'):
                        if isCurrent:
                            toolTempDesired = float(tokens[index][1:])
                        index += 1

                elif tokens[index] == 'B':
                    if isCurrent:
                        bedTempActual = float(tokens[index+1])
                    index += 2

                    if tokens[index].startswith('/'):
                        bedTempDesired = float(tokens[index][1:])
                        index += 1

                elif tokens[index] == 'C':
                    index += 2
                    if tokens[index].startswith('/'):
                        index += 1

                elif tokens[index].startswith('@'):
                    if tokens[index] == '@':
                        toolPower = float(tokens[index+1])
                    index += 2

                elif tokens[index] == 'B@':
                    bedPower = float(tokens[index+1])
                    index += 2

                elif tokens[index] == 'P':
                    index += 2

                elif tokens[index] == 'A':
                    index += 2

                else:
                    raise GCodeError(f'Unable to parse response: [{line}].')
        except IndexError as exception:
            raise GCodeError(f'Unable to parse response: [{line}].') from exception
        except ValueError as exception:
            raise GCodeError(f'Incorrect numeric data type found in response: [{line}].') from exception

        self.result = {'toolActual':  toolTempActual,
                       'toolDesired': toolTempDesired,
                       'bedActual':   bedTempActual,
                       'bedDesired':  bedTempDesired,
                       'toolPower':   toolPower,
                       'bedPower':    bedPower}

        return True