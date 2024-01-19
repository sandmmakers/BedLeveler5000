from .OkCommand import OkCommand

class CommandM400(OkCommand):
    NAME = 'M400'

    def __init__(self):
        # Build request
        super().__init__(self.NAME)