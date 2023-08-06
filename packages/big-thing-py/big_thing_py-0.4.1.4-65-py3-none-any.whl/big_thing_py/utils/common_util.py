from big_thing_py.common.common import *

import inspect
import socket
import json
import time
import copy
import os
from pathlib import Path
import getmac


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


def get_function_return_type(func: Callable):
    return func.__annotations__['return']


def get_function_parameter(func: Callable):
    annotations_copy = copy.deepcopy(func.__annotations__)
    annotations_copy.pop('return')
    return annotations_copy


def get_ip_from_url(URL: str):
    return socket.gethostbyname(URL)


def get_mac_address():
    return str(getmac.get_mac_address()).replace(':', '').upper()


def get_current_time(mode: TimeFormat = TimeFormat.UNIXTIME):
    if mode == TimeFormat.DATETIME1:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    elif mode == TimeFormat.DATETIME2:
        return time.strftime("%Y%m%d_%H%M%S", time.localtime())
    elif mode == TimeFormat.DATE:
        return time.strftime("%Y-%m-%d", time.localtime())
    elif mode == TimeFormat.TIME:
        return time.strftime("%H:%M:%S", time.localtime())
    elif mode == TimeFormat.UNIXTIME:
        return time.time()
    return time.time()


def type_converter(in_type: Union[SoPType, type, str, None]) -> Union[type, SoPType]:
    if type(in_type) == SoPType:
        if in_type in (SoPType.BINARY, SoPType.STRING):
            return str
        elif in_type == SoPType.BOOL:
            return bool
        elif in_type == SoPType.DOUBLE:
            return float
        elif in_type == SoPType.INTEGER:
            return int
        elif in_type in (SoPType.VOID, SoPType.UNDEFINED):
            return None
        else:
            raise SoPTypeError('Unexpected python type!!!')
    elif type(in_type) == type:
        if in_type == int:
            return SoPType.INTEGER
        elif in_type == float:
            return SoPType.DOUBLE
        elif in_type == bool:
            return SoPType.BOOL
        elif in_type == bytes:
            return SoPType.BINARY
        elif in_type == str:
            return SoPType.STRING
        elif in_type == type(None):
            return SoPType.VOID
        else:
            raise SoPTypeError('Unexpected SoPType type!!!')
    elif type(in_type) == str:
        if in_type == 'int':
            return SoPType.INTEGER
        elif in_type == 'void':
            return SoPType.VOID
        elif in_type == 'double':
            return SoPType.DOUBLE
        elif in_type == 'bool':
            return SoPType.BOOL
        elif in_type == 'binary':
            return SoPType.BINARY
        elif in_type == 'string':
            return SoPType.STRING
        elif in_type == 'undefined':
            return SoPType.UNDEFINED
        else:
            raise SoPTypeError('Unexpected SoPType type!!!')
    elif in_type == None or type(in_type) == type(None):
        return SoPType.VOID


def get_current_function_name():
    return inspect.currentframe().f_back.f_code.co_name


# TODO: need to be implement recursively
def get_upper_function_name(step: int = 1):
    if step == 1:
        return inspect.currentframe().f_back.f_back.f_code.co_name
    elif step == 2:
        return inspect.currentframe().f_back.f_back.f_back.f_code.co_name
    elif step == 3:
        return inspect.currentframe().f_back.f_back.f_back.f_back.f_code.co_name
    elif step == 4:
        return inspect.currentframe().f_back.f_back.f_back.f_back.f_back.f_code.co_name
    else:
        print('too many steps... return MAX upper function name')
        return inspect.currentframe().f_back.f_back.f_back.f_back.f_back.f_code.co_name


def json_file_read(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return False


def json_file_write(path, data, indent: int = 4):
    with open(path, 'w') as f:
        if isinstance(data, (dict, str)):
            json.dump(data, f, indent=indent)
        else:
            raise Exception(
                f'common_util.json_file_write: data type error - {type(data)}')


def get_project_root(project_name: str = 'big-thing-py') -> Path:
    start_path = Path(__file__)
    while True:
        if str(start_path).split('/')[-1] == project_name:
            return str(start_path)
        else:
            start_path = start_path.parent
