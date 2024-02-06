from Printers.Marlin2.Commands.CommandM118 import CommandM118
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    a1: bool = field(default=False)
    e1: bool = field(default=False)
    pn: Union[None, int] = field(default=None)
    string: Union[None, int] = field(default=None)
    expected: dict = field(default=None)

testPoints = [
    TestPoint(string = '123abc',
              lines = ['123abc\r',
                       'ok P15 B3'],
              expected = {'string': '123abc'}),
    TestPoint(a1 = True,
              string = '123abc',
              lines = ['//123abc\r',
                       'ok P15 B3'],
              expected = {'string': '//123abc'}),
    TestPoint(e1 = True,
              string = '123abc',
              lines = ['echo:123abc\r',
                       'ok P15 B3'],
              expected = {'string': 'echo:123abc'})
    ]

def createCommandM118(testPoint):
    return CommandM118(a1 = testPoint.a1,
                       e1 = testPoint.e1,
                       pn = testPoint.pn,
                       string = testPoint.string)

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandM118 = createCommandM118(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandM118._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandM118.result == testPoint.expected)