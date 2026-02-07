from .Common import LOG_ALL
from .Common import toArgumentString
import logging
import wrapt

def loggedFunction(wrapped=None, *, level=logging.INFO):
    if wrapped is None:
        return wrapt.PartialCallableObjectProxy(loggedFunction, level=level)

    if isinstance(level, str):
        upper = level.upper()
        level = LOG_ALL if upper == 'ALL' else getattr(logging, upper)

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        className, dot, functionName = wrapped.__qualname__.rpartition('.')
        logger = logging.getLogger(className)
        argumentString = toArgumentString(args, kwargs)
        logger.log(level, f'{functionName}({argumentString})')
        return wrapped(*args, **kwargs)

    # pylint: disable-next=no-value-for-parameter
    return wrapper(wrapped)

if __name__ == '__main__':
    from .Common import configureLogging

    configureLogging(level='debug', console='True')
    logger = logging.getLogger()

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

    @loggedFunction(level=LOG_ALL)
    def MyAllFunctionConst():
        pass
    MyAllFunctionConst()

    @loggedFunction(level='all')
    def MyAllFunctionStr():
        pass
    MyAllFunctionStr()

    @loggedFunction
    @staticmethod
    def MyStaticFunction0():
        pass
    MyStaticFunction0()

    @loggedFunction
    @staticmethod
    def MyStaticFunction2(a, b):
        pass
    MyStaticFunction2(1, 2)

    class MyClass:
        @loggedFunction
        def myMemberFunction(self, a, b, *, c, d):
            pass
    myClass = MyClass()
    myClass.myMemberFunction(1, 2, c=3, d=4)