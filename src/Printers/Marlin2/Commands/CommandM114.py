from .PositionOkCommand import PositionOkCommand

class CommandM114(PositionOkCommand):
    NAME = 'M114'

    def __init__(self, *, d=None, e=None, r=None):
        self.d = d
        self.e = e
        self.r = r

        dPart = ' D' if self.d else ''
        ePart = ' E' if self.e else ''
        rPart = ' R' if self.r else ''

        super().__init__(self.NAME + dPart + ePart + rPart)