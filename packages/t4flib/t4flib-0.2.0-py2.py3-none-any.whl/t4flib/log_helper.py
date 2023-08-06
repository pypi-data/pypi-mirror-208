"""
logger.py - un module pour logger des messages avec timestamp et couleur
"""

import datetime
from colorama import Fore, init
import inspect


def logger(severity, message):
    init()
    """Log un message avec une timestamp et une couleur selon la sévérité"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    frame_records = inspect.stack()[1:]
    indent = len(frame_records)

    indentation = '-' * 2 * indent

    if severity == 'INFO':
        color = Fore.GREEN
    elif severity == 'WARNING':
        color = Fore.YELLOW
    elif severity == 'ERROR':
        color = Fore.RED
    elif severity == 'DEBUG':
        color = Fore.BLUE
    else:
        color = Fore.WHITE

    print(
        f"|{indentation} [{timestamp}] - [{Fore.CYAN}{inspect.stack()[1].function}{Fore.RESET}] - "
        f"[{color}{severity}{Fore.RESET}] {message}")
