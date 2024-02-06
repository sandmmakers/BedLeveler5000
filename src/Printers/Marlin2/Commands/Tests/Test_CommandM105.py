from Printers.Marlin2.Commands.CommandM105 import CommandM105
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    r: bool = field(default=False)
    t: Union[None, int] = field(default=None)
    expected: dict = field(default=None)

testPoints = [
    TestPoint(lines = ['ok T:127.97 /12.00 B:25.00 /0.00 @:12.2 B@:21.2'],
              expected = {'toolActual': 127.97,
                          'toolDesired': 12.00,
                          'bedActual':   25.00,
                          'bedDesired':   0.00,
                          'toolPower':   12.20,
                          'bedPower':    21.20}),
    TestPoint(lines = ['ok T0:245.00 /245.00 B:70.01 /70.00 T0:245.00 /245.00 T1:18.83 /0.00 @:58 B@:52 @0:58 @1:0'],
              expected = {'toolActual':  245.00,
                          'toolDesired': 245.00,
                          'bedActual':    70.01,
                          'bedDesired':   70.00,
                          'toolPower':    58.00,
                          'bedPower':     52.00}),
    TestPoint(lines = ['ok T:245.00 /245.00 B:70.01 /70.00 T0:245.00 /245.00 T1:18.83 /0.00 @:58 B@:52 @0:58 @1:0'],
              expected = {'toolActual':  245.00,
                          'toolDesired': 245.00,
                          'bedActual':    70.01,
                          'bedDesired':   70.00,
                          'toolPower':    58.00,
                          'bedPower':     52.00}),
                          
    #SENT: 'M105 T1'
    #RECV: 'echo:M105 Invalid extruder 1'
    ]

def createCommandM105(testPoint):
    return CommandM105(r = testPoint.r,
                       t = testPoint.t)

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandM105 = createCommandM105(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandM105._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandM105.result == testPoint.expected)