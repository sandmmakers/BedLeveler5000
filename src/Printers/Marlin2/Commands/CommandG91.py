from .OkCommand import OkCommand

class CommandG91(OkCommand):
    NAME = 'G91'

    def __init__(self):
        super().__init__(self.NAME)