import typing

class StrOptional:
    def __init__(self, messageArg: typing.Optional[str] = None):
        self._message = messageArg

    def __str__(self):
        return 'None' if self._message is None else self._message

    def __bool__(self):
        return self.hasValue()

    def hasValue(self):
        return self._message is not None

    def message(self):
        return self._message