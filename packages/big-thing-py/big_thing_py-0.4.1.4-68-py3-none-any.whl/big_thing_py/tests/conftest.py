from big_thing_py.big_thing import *

import pytest


class ReturnValue_Function():
    int_value = None
    float_value = None
    str_value = None
    bool_value = None
    binary_value = None
    call_cnt = 0

    def __init__(self, value: Union[int, float, str, bool] = None):
        if value is not None:
            if type(value) == int:
                ReturnValue_Function.int_value = value
            elif type(value) == float:
                ReturnValue_Function.float_value = value
            elif type(value) == str:
                ReturnValue_Function.str_value = value
            elif type(value) == bool:
                ReturnValue_Function.bool_value = value
            elif type(value) == str and self.isBase64(value):
                ReturnValue_Function.binary_value = value
        elif ReturnValue_Function.call_cnt == 0:
            ReturnValue_Function.int_value = 0
            ReturnValue_Function.float_value = 0.0
            ReturnValue_Function.str_value = str(0)
            ReturnValue_Function.bool_value = True
            ReturnValue_Function.binary_value = string_to_base64(str(0))

        ReturnValue_Function.call_cnt += 1

    def isBase64(self, s):
        import base64
        try:
            return base64.b64encode(base64.b64decode(s)) == s
        except Exception:
            return False


class ReturnValue_Value():
    int_value = None
    float_value = None
    str_value = None
    bool_value = None
    binary_value = None
    call_cnt = 0

    def __init__(self, value: Union[int, float, str, bool] = None):
        if value is not None:
            if type(value) == int:
                ReturnValue_Value.int_value = value
            elif type(value) == float:
                ReturnValue_Value.float_value = value
            elif type(value) == str:
                ReturnValue_Value.str_value = value
            elif type(value) == bool:
                ReturnValue_Value.bool_value = value
            elif type(value) == str and self.isBase64(value):
                ReturnValue_Value.binary_value = value
        elif ReturnValue_Value.call_cnt == 0:
            ReturnValue_Value.int_value = 0
            ReturnValue_Value.float_value = 0.0
            ReturnValue_Value.str_value = str(0)
            ReturnValue_Value.bool_value = True
            ReturnValue_Value.binary_value = string_to_base64(str(0))

        ReturnValue_Value.call_cnt += 1

    def isBase64(self, s):
        import base64
        try:
            return base64.b64encode(base64.b64decode(s)) == s
        except Exception:
            return False


# ----------------------------------------------------------------------------------------------------------------------

def fail_function() -> int:
    raise Exception('fail function')


def int_function_no_arg_timeout_3() -> int:
    ReturnValue_Function()
    ReturnValue_Function.int_value += 1

    time.sleep(5)

    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. return {ReturnValue_Function.int_value}', 'green')
    return ReturnValue_Function.int_value


def int_function_no_arg_with_delay_1() -> int:
    ReturnValue_Function()
    ReturnValue_Function.int_value += 1

    time.sleep(1)

    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. return {ReturnValue_Function.int_value}', 'green')
    return ReturnValue_Function.int_value


def int_function_no_arg() -> int:
    ReturnValue_Function()
    ReturnValue_Function.int_value += 1
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. return {ReturnValue_Function.int_value}', 'green')
    return ReturnValue_Function.int_value


def float_function_no_arg() -> float:
    ReturnValue_Function()
    ReturnValue_Function.float_value += 1.0
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. return {ReturnValue_Function.float_value}', 'green')
    return ReturnValue_Function.float_value


def str_function_no_arg() -> str:
    ReturnValue_Function()
    ReturnValue_Function.str_value = str(
        int(ReturnValue_Function.str_value) + 1)
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. return {ReturnValue_Function.str_value}', 'green')
    return ReturnValue_Function.str_value


def bool_function_no_arg() -> bool:
    ReturnValue_Function()
    ReturnValue_Function.bool_value = ReturnValue_Function.int_value % 2 == 0
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. return {ReturnValue_Function.bool_value}', 'green')
    return ReturnValue_Function.bool_value


# def binary_function_no_arg() -> str:
#     ReturnValue()
#     return_value = ReturnValue()
#     ReturnValue.binary_value = string_to_base64(
#         str(int(ReturnValue.binary_value) + 1))
#     SOPLOG_DEBUG(
#         f'{get_current_function_name()} run. return {ReturnValue.binary_value}', 'green')
#     return ReturnValue.binary_value


def void_function_no_arg() -> None:
    SOPLOG_DEBUG(f'{get_current_function_name()} run. no return', 'green')

# ----------------------------------------------------------------------------------------------------------------------


def int_value_return_5() -> int:
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. return {5}', 'green')
    return 5


def int_value_no_arg() -> int:
    ReturnValue_Value()
    ReturnValue_Value.int_value += 1
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. return {ReturnValue_Value.int_value}', 'green')
    return ReturnValue_Value.int_value


def float_value_no_arg() -> float:
    ReturnValue_Value()
    ReturnValue_Value.float_value += 1.0
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. return {ReturnValue_Value.float_value}', 'green')
    return ReturnValue_Value.float_value


def str_value_no_arg() -> str:
    ReturnValue_Value()
    ReturnValue_Value.str_value = str(
        int(ReturnValue_Value.str_value) + 1)
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. return {ReturnValue_Value.str_value}', 'green')
    return ReturnValue_Value.str_value


def bool_value_no_arg() -> bool:
    ReturnValue_Value()
    ReturnValue_Value.bool_value = ReturnValue_Value.int_value % 2 == 0
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. return {ReturnValue_Value.bool_value}', 'green')
    return ReturnValue_Value.bool_value


# def binary_function_no_arg() -> str:
#     ReturnValue()
#     return_value = ReturnValue()
#     ReturnValue.binary_value = string_to_base64(
#         str(int(ReturnValue.binary_value) + 1))
#     SOPLOG_DEBUG(
#         f'{get_current_function_name()} run. return {ReturnValue.binary_value}', 'green')
#     return ReturnValue.binary_value


def void_value_no_arg() -> None:
    SOPLOG_DEBUG(f'{get_current_function_name()} run. no return', 'green')

# ----------------------------------------------------------------------------------------------------------------------


def int_function_with_arg(int_arg: int) -> int:
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. argument : {int_arg}, return {int_arg}', 'green')
    return int_arg


def float_function_with_arg(float_arg: int) -> float:
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. argument : {float_arg}, return {float_arg}', 'green')
    return float_arg


def str_function_with_arg(str_arg: int) -> str:
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. argument : {str_arg}, return {str_arg}', 'green')
    return str_arg


def bool_function_with_arg(bool_arg: int) -> bool:
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. argument : {bool_arg}, return {bool_arg}', 'green')
    return bool_arg


# def binary_function_with_arg(binary_arg: int) -> str:
#     SOPLOG_DEBUG(
#         f'{get_current_function_name()} run. argument : {binary_arg}, return {binary_arg}', 'green')
#     return binary_arg


def void_function_with_arg(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> None:
    SOPLOG_DEBUG(
        f'{get_current_function_name()} run. argument : {int_arg}, {float_arg}, {str_arg}, {bool_arg} no return.', 'green')

# def void_function_with_arg(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool, binary_arg: str) -> None:
#     SOPLOG_DEBUG(
#         f'{get_current_function_name()} run. argument : {int_arg}, {float_arg}, {str_arg}, {bool_arg}, {binary_arg} no return.', 'green')

# ----------------------------------------------------------------------------------------------------------------------


def generate_thing(name: str, ip: str, port: int, alive_cycle: float) -> SoPBigThing:
    alive_cycle = 1
    value_cycle = alive_cycle

    tag_list = [SoPTag('full')]

    int_arg_list = [SoPArgument(name='int_arg',
                                type=SoPType.INTEGER,
                                bound=(-2147483648, 2147483647)), ]
    float_arg_list = [SoPArgument(name='float_arg',
                                  type=SoPType.DOUBLE,
                                  bound=(-2147483648, 2147483647)), ]
    str_arg_list = [SoPArgument(name='str_arg',
                                type=SoPType.STRING,
                                bound=(-2147483648, 2147483647)), ]
    bool_arg_list = [SoPArgument(name='bool_arg',
                                 type=SoPType.BOOL,
                                 bound=(-2147483648, 2147483647)), ]
    binary_arg_list = [SoPArgument(name='binary_arg',
                                   type=SoPType.BINARY,
                                   bound=(-2147483648, 2147483647))]
    full_arg_list = [SoPArgument(name='int_arg',
                                 type=SoPType.INTEGER,
                                 bound=(-2147483648, 2147483647)),
                     SoPArgument(name='float_arg',
                                 type=SoPType.DOUBLE,
                                 bound=(-2147483648, 2147483647)),
                     SoPArgument(name='str_arg',
                                 type=SoPType.STRING,
                                 bound=(-2147483648, 2147483647)),
                     SoPArgument(name='bool_arg',
                                 type=SoPType.BOOL,
                                 bound=(-2147483648, 2147483647)),
                     # SoPArgument(name='binary_arg',
                     #             type=SoPType.BINARY,
                     #             bound=(-2147483648, 2147483647))
                     ]

    value_list = [
        SoPValue(name='int_value_return_5',
                 func=int_value_return_5,
                 type=SoPType.INTEGER,
                 bound=(-2147483648, 2147483647),
                 tag_list=tag_list + [SoPTag('INTEGER')],
                 cycle=value_cycle),
        SoPValue(name='int_value',
                 func=int_value_no_arg,
                 type=SoPType.INTEGER,
                 bound=(-2147483648, 2147483647),
                 tag_list=tag_list + [SoPTag('INTEGER')],
                 cycle=value_cycle),
        SoPValue(name='float_value',
                 func=float_value_no_arg,
                 type=SoPType.DOUBLE,
                 bound=(-2147483648, 2147483647),
                 tag_list=tag_list + [SoPTag('DOUBLE')],
                 cycle=value_cycle),
        SoPValue(name='str_value',
                 func=str_value_no_arg,
                 type=SoPType.STRING,
                 bound=(-2147483648, 2147483647),
                 tag_list=tag_list + [SoPTag('STRING')],
                 cycle=value_cycle),
        SoPValue(name='bool_value',
                 func=bool_value_no_arg,
                 type=SoPType.BOOL,
                 bound=(-2147483648, 2147483647),
                 tag_list=tag_list + [SoPTag('BOOL')],
                 cycle=value_cycle),
        # SoPValue(name='binary_value',
        #          func=binary_function_no_arg,
        #          type=SoPType.BINARY,
        #          bound=(-2147483648, 2147483647),
        #          tag_list=default_tag_list + value_tag_list + [SoPTag('BINARY')],
        #          cycle=value_cycle)
    ]

    no_arg_function_list = [
        SoPFunction(name='fail_function',
                    func=fail_function,
                    return_type=SoPType.INTEGER,
                    desc='fail_function',
                    tag_list=tag_list + [SoPTag('INTEGER')],
                    arg_list=[],
                    exec_time=1,
                    timeout=1,
                    policy=SoPPolicy.SINGLE,
                    energy=10),
        SoPFunction(name='int_function_no_arg_timeout_3',
                    func=int_function_no_arg_timeout_3,
                    return_type=SoPType.INTEGER,
                    desc='int_function_no_arg_timeout_3',
                    tag_list=tag_list + [SoPTag('INTEGER')],
                    arg_list=[],
                    exec_time=1,
                    timeout=3,
                    policy=SoPPolicy.SINGLE,
                    energy=10),
        SoPFunction(name='int_function_no_arg_with_delay_1',
                    func=int_function_no_arg_with_delay_1,
                    return_type=SoPType.INTEGER,
                    desc='int_function_no_arg_with_delay_1',
                    tag_list=tag_list + [SoPTag('INTEGER')],
                    arg_list=[],
                    exec_time=1,
                    timeout=1,
                    policy=SoPPolicy.SINGLE,
                    energy=10),
        SoPFunction(name='int_function_no_arg',
                    func=int_function_no_arg,
                    return_type=SoPType.INTEGER,
                    desc='int_function_no_arg',
                    tag_list=tag_list + [SoPTag('INTEGER')],
                    arg_list=[],
                    exec_time=1,
                    timeout=1,
                    policy=SoPPolicy.SINGLE,
                    energy=10),
        SoPFunction(name='float_function_no_arg',
                    func=float_function_no_arg,
                    return_type=SoPType.DOUBLE,
                    desc='float_function_no_arg',
                    tag_list=tag_list + [SoPTag('DOUBLE')],
                    arg_list=[],
                    exec_time=1,
                    timeout=1,
                    policy=SoPPolicy.SINGLE,
                    energy=10),
        SoPFunction(name='str_function_no_arg',
                    func=str_function_no_arg,
                    return_type=SoPType.STRING,
                    desc='str_function_no_arg',
                    tag_list=tag_list + [SoPTag('STRING')],
                    arg_list=[],
                    exec_time=1,
                    timeout=1,
                    policy=SoPPolicy.SINGLE,
                    energy=10),
        SoPFunction(name='bool_function_no_arg',
                    func=bool_function_no_arg,
                    return_type=SoPType.BOOL,
                    desc='bool_function_no_arg',
                    tag_list=tag_list + [SoPTag('BOOL')],
                    arg_list=[],
                    exec_time=1,
                    timeout=1,
                    policy=SoPPolicy.SINGLE,
                    energy=10),
        # SoPFunction(name='binary_function_no_arg',
        #             func=binary_function_no_arg,
        #             return_type=SoPType.BINARY,
        #             desc='binary_function_no_arg',
        #             tag_list=default_tag_list +
        #             [SoPTag('BINARY')],
        #             arg_list=[],
        #             exec_time=1,
        #             timeout=1,
        #             policy=SoPPolicy.SINGLE),
        SoPFunction(name='void_function_no_arg',
                    func=void_function_no_arg,
                    return_type=SoPType.VOID,
                    desc='void_function_no_arg',
                    tag_list=tag_list + [SoPTag('VOID')],
                    arg_list=[],
                    exec_time=1,
                    timeout=1,
                    policy=SoPPolicy.SINGLE,
                    energy=10)
    ]
    arg_function_list = [
        SoPFunction(name='int_function_with_arg',
                    func=int_function_with_arg,
                    return_type=SoPType.INTEGER,
                    desc='int_function_with_arg',
                    tag_list=tag_list + [SoPTag('INTEGER')],
                    arg_list=int_arg_list,
                    exec_time=1,
                    timeout=1,
                    policy=SoPPolicy.SINGLE,
                    energy=20),
        SoPFunction(name='float_function_with_arg',
                    func=float_function_with_arg,
                    return_type=SoPType.DOUBLE,
                    desc='float_function_with_arg',
                    tag_list=tag_list + [SoPTag('DOUBLE')],
                    arg_list=float_arg_list,
                    exec_time=1,
                    timeout=1,
                    policy=SoPPolicy.SINGLE,
                    energy=20),
        SoPFunction(name='str_function_with_arg',
                    func=str_function_with_arg,
                    return_type=SoPType.STRING,
                    desc='str_function_with_arg',
                    tag_list=tag_list + [SoPTag('STRING')],
                    arg_list=str_arg_list,
                    exec_time=1,
                    timeout=1,
                    policy=SoPPolicy.SINGLE,
                    energy=20),
        SoPFunction(name='bool_function_with_arg',
                    func=bool_function_with_arg,
                    return_type=SoPType.BOOL,
                    desc='bool_function_with_arg',
                    tag_list=tag_list + [SoPTag('BOOL')],
                    arg_list=bool_arg_list,
                    exec_time=1,
                    timeout=1,
                    policy=SoPPolicy.SINGLE,
                    energy=20),
        # SoPFunction(name='binary_function_with_arg',
        #             func=binary_function_with_arg,
        #             return_type=SoPType.BINARY,
        #             desc='binary_function_with_arg',
        #             tag_list=default_tag_list +
        #             [SoPTag('BINARY')],
        #             arg_list=arg_list,
        #             exec_time=1,
        #             timeout=1,
        #             policy=SoPPolicy.SINGLE),
        SoPFunction(name='void_function_with_arg',
                    func=void_function_with_arg,
                    return_type=SoPType.VOID,
                    desc='void_function_with_arg',
                    tag_list=tag_list + [SoPTag('VOID')],
                    arg_list=full_arg_list,
                    exec_time=1,
                    timeout=1,
                    policy=SoPPolicy.SINGLE,
                    energy=20)
    ]
    thing = SoPBigThing(name=name, ip=ip, port=port, alive_cycle=alive_cycle,
                        service_list=value_list + no_arg_function_list + arg_function_list, append_mac_address=False)
    return thing


@pytest.fixture
def full_feature_big_thing() -> SoPBigThing:
    big_thing = generate_thing(
        name='test_thing', ip='localhost', port=1883, alive_cycle=60)
    return big_thing
