import logging
import pathlib
import sys

LOG_ALL = 1
LOG_NONE = 99

# Determine the effective base directory
def baseDir():
    return pathlib.Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else pathlib.Path(__file__).parent.parent.parent

def configureLogging(level=None, console=False, file=None):
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    if level is None:
        logLevelValue = LOG_NONE
    elif isinstance(level, int):
        logLevelValue = level
    else:
        if level.upper() == 'ALL':
            logLevelValue = LOG_ALL
        else:
            logLevelValue = getattr(logging, level.upper())

    logger = logging.getLogger()
    logger.setLevel(logLevelValue)
    formatter = logging.Formatter(LOGGING_FORMAT)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logLevelValue if console else LOG_NONE)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    if file is not None:
        fileHandler = logging.FileHandler(file)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)