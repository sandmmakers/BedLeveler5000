from .OkCommand import OkCommand

class CommandG90(OkCommand):
    NAME = 'G90'

    def __init__(self):
        super().__init__(self.NAME)