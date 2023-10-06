import logging
import pathlib
import sys

# Determine the effective base directory
def baseDir():
    return pathlib.Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else pathlib.Path(__file__).parent.parent

def configureLogging(level=None, console=False, file=None):
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logger = logging.getLogger()
    logger.setLevel(99 if level is None else getattr(logging, level.upper()))
    formatter = logging.Formatter(LOGGING_FORMAT)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logger.level if console else 99)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    if file is not None:
        fileHandler = logging.FileHandler(file)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)