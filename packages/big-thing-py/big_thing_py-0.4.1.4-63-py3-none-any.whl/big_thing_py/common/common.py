from big_thing_py.common.error import *
from big_thing_py.common.soptype import *

from typing import *
from termcolor import *
from abc import *
from enum import Enum


EMPTY_JSON = '{}'
THREAD_TIME_OUT = 0.0001


class TimeFormat(Enum):
    DATETIME1 = '%Y-%m-%d %H:%M:%S'
    DATETIME2 = '%Y%m%d_%H%M%S'
    DATE = '%Y-%m-%d'
    TIME = '%H:%M:%S'
    UNIXTIME = 'unixtime'


class SoPPrintMode(Enum):
    UNDEFINED = 'undefined'
    FULL = 'full'
    ABBR = 'abbr'
    SKIP = 'skip'

    @classmethod
    def get(cls, name: str):
        try:
            return cls[name.upper()]
        except Exception:
            return cls.UNDEFINED


class PrintTag:
    # MQTT protocol
    GOOD = '[%-30s]' % colored('✔✔✔', 'green')
    DUP = '[%-30s]' % colored('DUP✔', 'green')
    ERROR = '[%-30s]' % colored('✖✖✖', 'red')

    CONNECT = '[%-30s]' % colored('-> CONNECT', 'blue')
    DISCONNECT = '[%-30s]' % colored('-> DISCONNECT', 'blue')

    SUBSCRIBE = '[%-30s]' % colored('-> SUBSCRIBE', 'white')
    UNSUBSCRIBE = '[%-30s]' % colored('-> UNSUBSCRIBE', 'white')


class SoPPolicy(Enum):
    UNDEFINED = -1
    ALL = 'all'
    SINGLE = 'single'

    @classmethod
    def get(cls, name: str):
        try:
            return cls[name.upper()]
        except Exception:
            return cls.UNDEFINED
