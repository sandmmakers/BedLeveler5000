from .Common import LOG_ALL
import functools
import logging
import types

def loggedFunction(helper=None, level=logging.INFO):
    assert callable(helper) or helper is None
    if level is None:
        level == LOG_ALL
    elif isinstance(level, str):
        upper = level.upper()
        level = LOG_ALL if upper == 'ALL' else getattr(logging, level.upper())

    def wrap(function):
        @functools.wraps(function)
        def logFunction(*args, **kwargs):
            className, dot, functionName = function.__qualname__.rpartition('.')
            logger = logging.getLogger(className)
            arguments = ''

            if len(args) > 0:
                argsStart = 0 if isinstance(function, types.FunctionType) == 0 else 1
                arguments = ', '.join(f'{v}' for v in args[argsStart:])

            if len(kwargs) > 0:
                if len(arguments) > 0:
                    arguments += ', '
                arguments += ", ".join(f'{k}={v}' for k, v in kwargs.items())

            logger.log(level, f'{functionName}({arguments})')
            return function(*args, **kwargs)
        return logFunction
    return wrap(helper) if callable(helper) else wrap

if __name__ == '__main__':
    from .Common import configureLogging

    configureLogging(level='debug', console='True')

    @loggedFunction
    def MyFunction0():
        pass
    MyFunction0()

    @loggedFunction
    def MyFunction2(a, b):
        pass
    MyFunction2(1, 2)

    @loggedFunction(level=logging.DEBUG)
    def MyDebugFunction():
        pass
    MyDebugFunction()

    @loggedFunction(level='all')
    def My1Function():
        pass
    My1Function()

    @staticmethod
    @loggedFunction
    def MyStaticFunction0():
        pass
    MyStaticFunction0()

    @staticmethod
    @loggedFunction
    def MyStaticFunction2(a, b):
        pass
    MyStaticFunction2(1, 2)

    class MyClass:
        @loggedFunction
        def myMemberFunction(self, a, b, *, c, d):
            pass
    myClass = MyClass()
    myClass.myMemberFunction(1, 2, c=3, d=4)