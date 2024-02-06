from Printers.Marlin2.Commands.CommandM420 import CommandM420
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    c: bool = field(default=False)
    l: Union[None, int] = field(default=None)
    s: bool = field(default=False)
    t: Union[None, int] = field(default=None)
    v: bool = field(default=False)
    z: Union[None, float] = field(default=None)
    expected: dict = field(default=None)

testPoints = [
    #SENT: 'M420'
    #RECV: 'echo:Bed Leveling OFF'
    #RECV: 'echo:Fade Height 10.00
    #'
    #RECV: 'ok P15 B3'

    #SENT: 'M420 S1'
    #RECV: 'echo:Bed Leveling ON'
    #RECV: 'echo:Fade Height 10.00
    #'
    #RECV: 'ok P15 B3'

    #SENT: 'M420 S1'
    #RECV: 'echo:Invalid mesh.'
    #RECV: 'Error:Failed to enable Bed Leveling'
    #RECV: 'echo:Bed Leveling OFF'
    #RECV: 'echo:Fade Height 10.00
    #'
    #RECV: 'ok P15 B3'

    TestPoint(v = False,
              lines = ['Bilinear Leveling Grid:',
                       '      0      1      2',
                       ' 0 +0.000 +0.000 +0.000',
                       ' 1 +0.000 +0.000 +0.000',
                       ' 2 +0.000 +0.000 +0.000',
                       '',
                       'echo:Bed Leveling ON',
                       'echo:Fade Height 10.00\r',
                       'ok P15 B3'],
              expected = {'response': ['Bilinear Leveling Grid:',
                                       '      0      1      2',
                                       ' 0 +0.000 +0.000 +0.000',
                                       ' 1 +0.000 +0.000 +0.000',
                                       ' 2 +0.000 +0.000 +0.000',
                                       '',
                                       'echo:Bed Leveling ON',
                                       'echo:Fade Height 10.00\r']}),
    TestPoint(v = True,
              lines = ['Bilinear Leveling Grid:',
                       '      0      1      2',
                       ' 0 +0.000 +0.000 +0.000',
                       ' 1 +0.000 +0.000 +0.000',
                       ' 2 +0.000 +0.000 +0.000',
                       '',
                       'echo:Bed Leveling ON',
                       'echo:Fade Height 10.00\r',
                       'ok P15 B3'],
              expected = {'response': ['Bilinear Leveling Grid:',
                                       '      0      1      2',
                                       ' 0 +0.000 +0.000 +0.000',
                                       ' 1 +0.000 +0.000 +0.000',
                                       ' 2 +0.000 +0.000 +0.000',
                                       '',
                                       'echo:Bed Leveling ON',
                                       'echo:Fade Height 10.00\r']}),
    TestPoint(v = True,
              lines = ['Bilinear Leveling Grid:',
                       '      0      1      2',
                       ' 0 +0.000 +0.000 +0.000',
                       ' 1 +0.000 +0.000 +0.000',
                       ' 2 +0.000 +0.000 +0.000',
                       '',
                       'Subdivided with CATMULL ROM Leveling Grid:',
                       '        0        1        2        3        4        5        6',
                       ' 0 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                       ' 1 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                       ' 2 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                       ' 3 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                       ' 4 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                       ' 5 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                       ' 6 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                       '',
                       'echo:Bed Leveling ON',
                       'echo:Fade Height 10.00\r',
                       'ok P15 B3'],
              expected = {'response': ['Bilinear Leveling Grid:',
                                       '      0      1      2',
                                       ' 0 +0.000 +0.000 +0.000',
                                       ' 1 +0.000 +0.000 +0.000',
                                       ' 2 +0.000 +0.000 +0.000',
                                       '',
                                       'Subdivided with CATMULL ROM Leveling Grid:',
                                       '        0        1        2        3        4        5        6',
                                       ' 0 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                                       ' 1 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                                       ' 2 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                                       ' 3 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                                       ' 4 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                                       ' 5 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                                       ' 6 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000 +0.00000',
                                       '',
                                       'echo:Bed Leveling ON',
                                       'echo:Fade Height 10.00\r']})
    ]

def createCommandM420(testPoint):
    return CommandM420(c = testPoint.c,
                       l = testPoint.l,
                       s = testPoint.s,
                       t = testPoint.t,
                       v = testPoint.v,
                       z = testPoint.z)

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandM420 = createCommandM420(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandM420._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandM420.result == testPoint.expected)