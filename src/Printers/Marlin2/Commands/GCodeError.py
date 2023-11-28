class GCodeError(Exception):
    """G-code parsing error

    Attributes:
        message - Error message
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)