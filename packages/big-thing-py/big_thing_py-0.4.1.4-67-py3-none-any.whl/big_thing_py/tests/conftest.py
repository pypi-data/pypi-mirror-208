from big_thing_py.big_thing import *
from big_thing_py.tests.thing_factory import *

import pytest
import subprocess

PARAMETRIZE_STRING_OLD = 'test_id, input, expected_output, expected_exception_message'
PARAMETRIZE_STRING = 'test_id, input, expected_output'
START_LOGGER()

# ----------------------------------------------------------------------------------------------------------------------


def fail_function() -> int:
    raise Exception('fail function')


@static_vars(int_value=0)
def int_function_no_arg_timeout_3() -> int:
    int_function_no_arg_timeout_3.int_value += 1

    time.sleep(5)

    MXLOG_DEBUG(
        f'{get_current_function_name()} run. return {int_function_no_arg_timeout_3.int_value}', 'green')
    return int_function_no_arg_timeout_3.int_value


@static_vars(int_value=0)
def int_function_no_arg_with_delay_1() -> int:
    int_function_no_arg_with_delay_1.int_value += 1

    time.sleep(1)

    MXLOG_DEBUG(
        f'{get_current_function_name()} run. return {int_function_no_arg_with_delay_1.int_value}', 'green')
    return int_function_no_arg_with_delay_1.int_value


@static_vars(int_value=0)
def int_function_no_arg() -> int:
    int_function_no_arg.int_value += 1
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. return {int_function_no_arg.int_value}', 'green')
    return int_function_no_arg.int_value


@static_vars(float_value=0.0)
def float_function_no_arg() -> float:
    float_function_no_arg.float_value += 1.0
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. return {float_function_no_arg.float_value}', 'green')
    return float_function_no_arg.float_value


@static_vars(str_value=str(0))
def str_function_no_arg() -> str:
    str_function_no_arg.str_value = str(
        int(str_function_no_arg.str_value) + 1)
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. return {str_function_no_arg.str_value}', 'green')
    return str_function_no_arg.str_value


@static_vars(bool_value=True)
def bool_function_no_arg() -> bool:
    bool_function_no_arg.bool_value = bool_function_no_arg.int_value % 2 == 0
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. return {bool_function_no_arg.bool_value}', 'green')
    return bool_function_no_arg.bool_value


# def binary_function_no_arg() -> str:
#     ReturnValue()
#     return_value = ReturnValue()
#     ReturnValue.binary_value = string_to_base64(
#         str(int(ReturnValue.binary_value) + 1))
#     MXLOG_DEBUG(
#         f'{get_current_function_name()} run. return {ReturnValue.binary_value}', 'green')
#     return ReturnValue.binary_value


def void_function_no_arg() -> None:
    MXLOG_DEBUG(f'{get_current_function_name()} run. no return', 'green')

# ----------------------------------------------------------------------------------------------------------------------


def int_value_return_5() -> int:
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. return {5}', 'green')
    return 5


@static_vars(int_value=0)
def int_value_no_arg() -> int:
    int_value_no_arg.int_value += 1
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. return {int_value_no_arg.int_value}', 'green')
    return int_value_no_arg.int_value


@static_vars(float_value=0.0)
def float_value_no_arg() -> float:
    float_value_no_arg.float_value += 1.0
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. return {float_value_no_arg.float_value}', 'green')
    return float_value_no_arg.float_value


@static_vars(str_value=str(0))
def str_value_no_arg() -> str:
    str_value_no_arg.str_value = str(
        int(str_value_no_arg.str_value) + 1)
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. return {str_value_no_arg.str_value}', 'green')
    return str_value_no_arg.str_value


@static_vars(bool_value=True)
def bool_value_no_arg() -> bool:
    bool_value_no_arg.bool_value = bool_value_no_arg.int_value % 2 == 0
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. return {bool_value_no_arg.bool_value}', 'green')
    return bool_value_no_arg.bool_value


# def binary_function_no_arg() -> str:
#     ReturnValue()
#     return_value = ReturnValue()
#     ReturnValue.binary_value = string_to_base64(
#         str(int(ReturnValue.binary_value) + 1))
#     MXLOG_DEBUG(
#         f'{get_current_function_name()} run. return {ReturnValue.binary_value}', 'green')
#     return ReturnValue.binary_value


def void_value_no_arg() -> None:
    MXLOG_DEBUG(f'{get_current_function_name()} run. no return', 'green')

# ----------------------------------------------------------------------------------------------------------------------


def int_function_with_arg(int_arg: int) -> int:
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. argument : {int_arg}, return {int_arg}', 'green')
    return int_arg


def float_function_with_arg(float_arg: int) -> float:
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. argument : {float_arg}, return {float_arg}', 'green')
    return float_arg


def str_function_with_arg(str_arg: int) -> str:
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. argument : {str_arg}, return {str_arg}', 'green')
    return str_arg


def bool_function_with_arg(bool_arg: int) -> bool:
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. argument : {bool_arg}, return {bool_arg}', 'green')
    return bool_arg


# def binary_function_with_arg(binary_arg: int) -> str:
#     MXLOG_DEBUG(
#         f'{get_current_function_name()} run. argument : {binary_arg}, return {binary_arg}', 'green')
#     return binary_arg


def void_function_with_arg(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> None:
    MXLOG_DEBUG(
        f'{get_current_function_name()} run. argument : {int_arg}, {float_arg}, {str_arg}, {bool_arg} no return.', 'green')

# def void_function_with_arg(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool, binary_arg: str) -> None:
#     MXLOG_DEBUG(
#         f'{get_current_function_name()} run. argument : {int_arg}, {float_arg}, {str_arg}, {bool_arg}, {binary_arg} no return.', 'green')

# ----------------------------------------------------------------------------------------------------------------------


def generate_full_feature_thing(name: str, ip: str, port: int, alive_cycle: float) -> MXBigThing:
    alive_cycle = 1
    value_cycle = alive_cycle

    tag_list = [MXTag('full')]

    int_arg_list = [MXArgument(name='int_arg',
                               type=MXType.INTEGER,
                               bound=(-2147483648, 2147483647)), ]
    float_arg_list = [MXArgument(name='float_arg',
                                 type=MXType.DOUBLE,
                                 bound=(-2147483648, 2147483647)), ]
    str_arg_list = [MXArgument(name='str_arg',
                               type=MXType.STRING,
                               bound=(-2147483648, 2147483647)), ]
    bool_arg_list = [MXArgument(name='bool_arg',
                                type=MXType.BOOL,
                                bound=(-2147483648, 2147483647)), ]
    binary_arg_list = [MXArgument(name='binary_arg',
                                  type=MXType.BINARY,
                                  bound=(-2147483648, 2147483647))]
    full_arg_list = [MXArgument(name='int_arg',
                                type=MXType.INTEGER,
                                bound=(-2147483648, 2147483647)),
                     MXArgument(name='float_arg',
                                type=MXType.DOUBLE,
                                bound=(-2147483648, 2147483647)),
                     MXArgument(name='str_arg',
                                type=MXType.STRING,
                                bound=(-2147483648, 2147483647)),
                     MXArgument(name='bool_arg',
                                type=MXType.BOOL,
                                bound=(-2147483648, 2147483647)),
                     # MXArgument(name='binary_arg',
                     #             type=MXType.BINARY,
                     #             bound=(-2147483648, 2147483647))
                     ]

    value_list = [
        MXValue(name='int_value_return_5',
                func=int_value_return_5,
                type=MXType.INTEGER,
                bound=(-2147483648, 2147483647),
                tag_list=tag_list + [MXTag('INTEGER')],
                cycle=value_cycle),
        MXValue(name='int_value',
                func=int_value_no_arg,
                type=MXType.INTEGER,
                bound=(-2147483648, 2147483647),
                tag_list=tag_list + [MXTag('INTEGER')],
                cycle=value_cycle),
        MXValue(name='float_value',
                func=float_value_no_arg,
                type=MXType.DOUBLE,
                bound=(-2147483648, 2147483647),
                tag_list=tag_list + [MXTag('DOUBLE')],
                cycle=value_cycle),
        MXValue(name='str_value',
                func=str_value_no_arg,
                type=MXType.STRING,
                bound=(-2147483648, 2147483647),
                tag_list=tag_list + [MXTag('STRING')],
                cycle=value_cycle),
        MXValue(name='bool_value',
                func=bool_value_no_arg,
                type=MXType.BOOL,
                bound=(-2147483648, 2147483647),
                tag_list=tag_list + [MXTag('BOOL')],
                cycle=value_cycle),
        # MXValue(name='binary_value',
        #          func=binary_function_no_arg,
        #          type=MXType.BINARY,
        #          bound=(-2147483648, 2147483647),
        #          tag_list=default_tag_list + value_tag_list + [MXTag('BINARY')],
        #          cycle=value_cycle)
    ]

    no_arg_function_list = [
        MXFunction(name='fail_function',
                   func=fail_function,
                   return_type=MXType.INTEGER,
                   desc='fail_function',
                   tag_list=tag_list + [MXTag('INTEGER')],
                   arg_list=[],
                   exec_time=1,
                   timeout=1,
                   range_type=MXRangeType.SINGLE,
                   energy=10),
        MXFunction(name='int_function_no_arg_timeout_3',
                   func=int_function_no_arg_timeout_3,
                   return_type=MXType.INTEGER,
                   desc='int_function_no_arg_timeout_3',
                   tag_list=tag_list + [MXTag('INTEGER')],
                   arg_list=[],
                   exec_time=1,
                   timeout=3,
                   range_type=MXRangeType.SINGLE,
                   energy=10),
        MXFunction(name='int_function_no_arg_with_delay_1',
                   func=int_function_no_arg_with_delay_1,
                   return_type=MXType.INTEGER,
                   desc='int_function_no_arg_with_delay_1',
                   tag_list=tag_list + [MXTag('INTEGER')],
                   arg_list=[],
                   exec_time=1,
                   timeout=1,
                   range_type=MXRangeType.SINGLE,
                   energy=10),
        MXFunction(name='int_function_no_arg',
                   func=int_function_no_arg,
                   return_type=MXType.INTEGER,
                   desc='int_function_no_arg',
                   tag_list=tag_list + [MXTag('INTEGER')],
                   arg_list=[],
                   exec_time=1,
                   timeout=1,
                   range_type=MXRangeType.SINGLE,
                   energy=10),
        MXFunction(name='float_function_no_arg',
                   func=float_function_no_arg,
                   return_type=MXType.DOUBLE,
                   desc='float_function_no_arg',
                   tag_list=tag_list + [MXTag('DOUBLE')],
                   arg_list=[],
                   exec_time=1,
                   timeout=1,
                   range_type=MXRangeType.SINGLE,
                   energy=10),
        MXFunction(name='str_function_no_arg',
                   func=str_function_no_arg,
                   return_type=MXType.STRING,
                   desc='str_function_no_arg',
                   tag_list=tag_list + [MXTag('STRING')],
                   arg_list=[],
                   exec_time=1,
                   timeout=1,
                   range_type=MXRangeType.SINGLE,
                   energy=10),
        MXFunction(name='bool_function_no_arg',
                   func=bool_function_no_arg,
                   return_type=MXType.BOOL,
                   desc='bool_function_no_arg',
                   tag_list=tag_list + [MXTag('BOOL')],
                   arg_list=[],
                   exec_time=1,
                   timeout=1,
                   range_type=MXRangeType.SINGLE,
                   energy=10),
        # MXFunction(name='binary_function_no_arg',
        #             func=binary_function_no_arg,
        #             return_type=MXType.BINARY,
        #             desc='binary_function_no_arg',
        #             tag_list=default_tag_list +
        #             [MXTag('BINARY')],
        #             arg_list=[],
        #             exec_time=1,
        #             timeout=1,
        #             range_type=MXRangeType.SINGLE),
        MXFunction(name='void_function_no_arg',
                   func=void_function_no_arg,
                   return_type=MXType.VOID,
                   desc='void_function_no_arg',
                   tag_list=tag_list + [MXTag('VOID')],
                   arg_list=[],
                   exec_time=1,
                   timeout=1,
                   range_type=MXRangeType.SINGLE,
                   energy=10)
    ]
    arg_function_list = [
        MXFunction(name='int_function_with_arg',
                   func=int_function_with_arg,
                   return_type=MXType.INTEGER,
                   desc='int_function_with_arg',
                   tag_list=tag_list + [MXTag('INTEGER')],
                   arg_list=int_arg_list,
                   exec_time=1,
                   timeout=1,
                   range_type=MXRangeType.SINGLE,
                   energy=20),
        MXFunction(name='float_function_with_arg',
                   func=float_function_with_arg,
                   return_type=MXType.DOUBLE,
                   desc='float_function_with_arg',
                   tag_list=tag_list + [MXTag('DOUBLE')],
                   arg_list=float_arg_list,
                   exec_time=1,
                   timeout=1,
                   range_type=MXRangeType.SINGLE,
                   energy=20),
        MXFunction(name='str_function_with_arg',
                   func=str_function_with_arg,
                   return_type=MXType.STRING,
                   desc='str_function_with_arg',
                   tag_list=tag_list + [MXTag('STRING')],
                   arg_list=str_arg_list,
                   exec_time=1,
                   timeout=1,
                   range_type=MXRangeType.SINGLE,
                   energy=20),
        MXFunction(name='bool_function_with_arg',
                   func=bool_function_with_arg,
                   return_type=MXType.BOOL,
                   desc='bool_function_with_arg',
                   tag_list=tag_list + [MXTag('BOOL')],
                   arg_list=bool_arg_list,
                   exec_time=1,
                   timeout=1,
                   range_type=MXRangeType.SINGLE,
                   energy=20),
        # MXFunction(name='binary_function_with_arg',
        #             func=binary_function_with_arg,
        #             return_type=MXType.BINARY,
        #             desc='binary_function_with_arg',
        #             tag_list=default_tag_list +
        #             [MXTag('BINARY')],
        #             arg_list=arg_list,
        #             exec_time=1,
        #             timeout=1,
        #             range_type=MXRangeType.SINGLE),
        MXFunction(name='void_function_with_arg',
                   func=void_function_with_arg,
                   return_type=MXType.VOID,
                   desc='void_function_with_arg',
                   tag_list=tag_list + [MXTag('VOID')],
                   arg_list=full_arg_list,
                   exec_time=1,
                   timeout=1,
                   range_type=MXRangeType.SINGLE,
                   energy=20)
    ]
    thing = MXBigThing(name=name, ip=ip, port=port, alive_cycle=alive_cycle,
                       service_list=value_list + no_arg_function_list + arg_function_list, append_mac_address=False)
    return thing

####################################################################################################################################


class MXBasicSuperThing(MXSuperThing):

    def __init__(self, name: str = MXSuperThing.DEFAULT_NAME, service_list: List[MXService] = [], alive_cycle: float = 60, is_super: bool = True, is_parallel: bool = True,
                 ip: str = '127.0.0.1', port: int = 1883, ssl_ca_path: str = '', ssl_enable: bool = False,
                 log_name: str = None, log_enable: bool = True, log_mode: MXPrintMode = MXPrintMode.ABBR,
                 append_mac_address: bool = True,
                 refresh_cycle: float = 30):

        tag_list = [MXTag(name='super'),
                    MXTag(name='basic'),
                    MXTag(name='big_thing'),
                    MXTag(name='function')]
        int_arg = MXArgument(name='int_arg',
                             type=MXType.INTEGER,
                             bound=(0, 1000000))
        delay_arg = MXArgument(name='delay_arg',
                               type=MXType.DOUBLE,
                               bound=(0.0, 1000000.0))

        value_list = []
        function_list = [MXSuperFunction(func=self.super_func_execute_func_no_arg_SINGLE,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[],
                                         timeout=1,
                                         energy=100),
                         MXSuperFunction(func=self.super_func_execute_func_no_arg_ALL,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[],
                                         timeout=1,
                                         energy=100),
                         MXSuperFunction(func=self.super_func_execute_func_with_arg_SINGLE,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[int_arg],
                                         timeout=1,
                                         energy=100),
                         MXSuperFunction(func=self.super_func_execute_func_with_arg_ALL,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[int_arg],
                                         timeout=1,
                                         energy=100),
                         MXSuperFunction(func=self.super_func_execute_func_with_arg_and_delay_SINGLE,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[int_arg, delay_arg],
                                         timeout=1,
                                         energy=100),
                         MXSuperFunction(func=self.super_func_execute_func_with_arg_and_delay_ALL,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[int_arg, delay_arg],
                                         timeout=1,
                                         energy=100),
                         MXSuperFunction(func=self.super_func_get_value_current_time_SINGLE,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[],
                                         timeout=1,
                                         energy=100),
                         MXSuperFunction(func=self.super_func_get_value_current_time_ALL,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[],
                                         timeout=1,
                                         energy=100),
                         MXSuperFunction(func=self.super_multiple_sub_service_request1,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[int_arg, delay_arg],
                                         timeout=1,
                                         energy=100),
                         MXSuperFunction(func=self.super_multiple_sub_service_request2,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[int_arg, delay_arg],
                                         timeout=1,
                                         energy=100),
                         MXSuperFunction(func=self.super_multiple_sub_service_request_with_fixed_argument1,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[int_arg, delay_arg],
                                         timeout=1,
                                         energy=100),
                         MXSuperFunction(func=self.super_multiple_sub_service_request_with_fixed_argument2,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[int_arg, delay_arg],
                                         timeout=1,
                                         energy=100),
                         MXSuperFunction(func=self.super_multiple_sub_service_request_with_argument_pass,
                                         return_type=MXType.INTEGER,
                                         tag_list=tag_list,
                                         arg_list=[int_arg, delay_arg],
                                         timeout=1,
                                         energy=100), ]

        service_list = value_list + function_list
        super().__init__(name=name, service_list=service_list, alive_cycle=alive_cycle, is_super=is_super, is_parallel=is_parallel,
                         ip=ip, port=port, ssl_ca_path=ssl_ca_path, ssl_enable=ssl_enable,
                         log_name=log_name, log_enable=log_enable, log_mode=log_mode,
                         append_mac_address=append_mac_address,
                         refresh_cycle=refresh_cycle)

    def load_super_service_params(self, super_service_params_list: List[str]):
        for super_service_params in super_service_params_list:
            super_service = eval(f'MXSuperFunction({super_service_params})')
            self.add_service(super_service)

    def super_func_execute_func_no_arg_SINGLE(self) -> int:
        result_list = self.req(sub_service_name='func_no_arg', tag_list=['basic'], return_type=MXType.INTEGER,
                               service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)

        result_sum = 0
        if result_list:
            for result in result_list:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

    def super_func_execute_func_no_arg_ALL(self) -> int:
        result_list = self.req(sub_service_name='func_no_arg', tag_list=['basic'], return_type=MXType.INTEGER,
                               service_type=MXServiceType.FUNCTION, range_type=MXRangeType.ALL)

        result_sum = 0
        if result_list:
            for result in result_list:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

    def super_func_execute_func_with_arg_SINGLE(self, int_arg: int) -> int:
        result_list = self.req(sub_service_name='func_with_arg', tag_list=['basic'], arg_list=(int_arg, ),  return_type=MXType.INTEGER,
                               service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)

        result_sum = 0
        if result_list:
            for result in result_list:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

    def super_func_execute_func_with_arg_ALL(self, int_arg: int) -> int:
        result_list = self.req(sub_service_name='func_with_arg', tag_list=['basic'], arg_list=(int_arg, ), return_type=MXType.INTEGER,
                               service_type=MXServiceType.FUNCTION, range_type=MXRangeType.ALL)

        result_sum = 0
        if result_list:
            for result in result_list:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

    def super_func_execute_func_with_arg_and_delay_SINGLE(self, int_arg: int, delay: float) -> int:
        result_list = self.req(sub_service_name='func_with_arg_and_delay', tag_list=['basic'], arg_list=(int_arg, delay, ), return_type=MXType.INTEGER,
                               service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)

        result_sum = 0
        if result_list:
            for result in result_list:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

    def super_func_execute_func_with_arg_and_delay_ALL(self, int_arg: int, delay: float) -> int:
        result_list = self.req(sub_service_name='func_with_arg_and_delay', tag_list=['basic'], arg_list=(int_arg, delay, ), return_type=MXType.INTEGER,
                               service_type=MXServiceType.FUNCTION, range_type=MXRangeType.ALL)

        result_sum = 0
        if result_list:
            for result in result_list:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

    def super_func_get_value_current_time_SINGLE(self) -> int:
        result_list = self.req(sub_service_name='value_current_time', tag_list=['basic'], return_type=MXType.INTEGER,
                               service_type=MXServiceType.VALUE, range_type=MXRangeType.SINGLE)

        result_sum = 0
        if result_list:
            for result in result_list:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

    def super_func_get_value_current_time_ALL(self) -> int:
        result_list = self.req(sub_service_name='value_current_time', tag_list=['basic'], return_type=MXType.INTEGER,
                               service_type=MXServiceType.VALUE, range_type=MXRangeType.ALL)

        result_sum = 0
        if result_list:
            for result in result_list:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

    def super_multiple_sub_service_request1(self, int_arg: int, delay: float) -> int:
        result_list1 = self.req(sub_service_name='func_with_arg_and_delay', tag_list=['basic'], arg_list=(int_arg, delay, ), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)
        result_list2 = self.req(sub_service_name='func_with_arg', tag_list=['basic'], arg_list=(int_arg, ), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.ALL)
        result_list3 = self.req(sub_service_name='func_no_arg', tag_list=['basic'], arg_list=(), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.ALL)

        result_sum = 0
        if result_list1 and result_list2 and result_list3:
            for result in result_list1:
                result_sum += result['return_value']
            for result in result_list2:
                result_sum += result['return_value']
            for result in result_list3:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

    def super_multiple_sub_service_request2(self, int_arg: int, delay: float) -> int:
        result_list1 = self.req(sub_service_name='func_with_arg_and_delay', tag_list=['basic'], arg_list=(int_arg, delay, ), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)
        result_list2 = self.req(sub_service_name='func_with_arg', tag_list=['basic'], arg_list=(int_arg, ), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.ALL)
        result_list3 = self.req(sub_service_name='func_no_arg', tag_list=['basic'], arg_list=(), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.ALL)

        result_sum = 0
        if result_list1 and result_list2 and result_list3:
            for result in result_list1:
                result_sum += result['return_value']
            for result in result_list2:
                result_sum += result['return_value']
            for result in result_list3:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

    def super_multiple_sub_service_request_with_fixed_argument1(self, int_arg: int, delay: float) -> int:
        result_list1 = self.req(sub_service_name='func_with_arg', tag_list=['basic'], arg_list=(int_arg, ), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)
        result_list2 = self.req(sub_service_name='func_with_arg_and_delay', tag_list=['basic'], arg_list=(142, delay, ), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)
        result_list3 = self.req(sub_service_name='func_no_arg', tag_list=['basic'], arg_list=(), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)

        result_sum = 0
        if result_list1 and result_list2 and result_list3:
            for result in result_list1:
                result_sum += result['return_value']
            for result in result_list2:
                result_sum += result['return_value']
            for result in result_list3:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

    def super_multiple_sub_service_request_with_fixed_argument2(self, int_arg: int, delay: float) -> int:
        result_list1 = self.req(sub_service_name='func_with_arg', tag_list=['basic'], arg_list=(int_arg, ), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)
        result_list2 = self.req(sub_service_name='func_with_arg_and_delay', tag_list=['basic'], arg_list=(142, delay, ), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.ALL)
        result_list3 = self.req(sub_service_name='func_no_arg', tag_list=['basic'], arg_list=(), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)

        result_sum = 0
        if result_list1 and result_list2 and result_list3:
            for result in result_list1:
                result_sum += result['return_value']
            for result in result_list2:
                result_sum += result['return_value']
            for result in result_list3:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

    def super_multiple_sub_service_request_with_argument_pass(self, int_arg: int, delay: float) -> int:
        result_list1 = self.req(sub_service_name='func_with_arg', tag_list=['basic'], arg_list=(int_arg, ), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)
        result1 = result_list1[0]['return_value'] if result_list1 else 0
        result_list2 = self.req(sub_service_name='func_with_arg_and_delay', tag_list=['basic'], arg_list=(result1, delay, ), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.ALL)
        result_list3 = self.req(sub_service_name='func_with_arg', tag_list=['basic'], arg_list=(100, ), return_type=MXType.INTEGER,
                                service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)

        result_sum = 0
        if result_list1 and result_list2 and result_list3:
            for result in result_list1:
                result_sum += result['return_value']
            for result in result_list2:
                result_sum += result['return_value']
            for result in result_list3:
                result_sum += result['return_value']

            return result_sum
        else:
            return 0

####################################################################################################################################


@pytest.fixture
def full_feature_big_thing() -> MXBigThing:
    big_thing = generate_full_feature_thing(
        name='test_thing', ip='localhost', port=1883, alive_cycle=60)
    return big_thing


@pytest.fixture
def default_big_thing() -> MXBigThing:
    big_thing = BigThingFactory().create_default_thing()
    return big_thing


@pytest.fixture
def big_thing() -> MXBigThing:
    big_thing = MXBigThing()
    return big_thing


@pytest.fixture
def basic_super_thing() -> MXBasicSuperThing:
    super_thing = MXBasicSuperThing()
    return super_thing


@pytest.fixture
def super_thing() -> MXSuperThing:
    super_thing = MXSuperThing()
    return super_thing

# TODO: remove. do not connect to broker in thing sdk test


@pytest.fixture()
def run_mosquitto():
    mosquitto_process = subprocess.Popen(
        ['mosquitto'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    yield mosquitto_process
    mosquitto_process.terminate()
    mosquitto_process.wait()


@pytest.fixture()
def run_ssl_mosquitto():
    mosquitto_process = subprocess.Popen(
        ['mosquitto', '-c', f'{get_project_root()}/res/mosquitto.conf'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    yield mosquitto_process
    mosquitto_process.terminate()
    mosquitto_process.wait()


@pytest.fixture()
def install_CA():
    result = subprocess.Popen([f'cp {get_project_root()}/res/CA/ca.crt /tmp/mosquitto/ca_certificates;'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = subprocess.Popen([f'cp {get_project_root()}/res/CA/host.crt /tmp/mosquitto/certs;',], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = subprocess.Popen([f'cp {get_project_root()}/res/CA/host.key /tmp/mosquitto/certs;',], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = subprocess.Popen([f'chmod -R 707 {get_project_root()}/res/CA/certs;',], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = subprocess.Popen([f'chmod -R 707 {get_project_root()}/res/CA/ca_certificates;'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result


def compare_mqtt_msg(output_msg: mqtt.MQTTMessage, expected_msg: mqtt.MQTTMessage):
    # if not isinstance(output_msg,  mqtt.MQTTMessage) or not isinstance(expected_msg, mqtt.MQTTMessage):
    #     return output_msg == expected_msg

    topic_check = (decode_MQTT_message(output_msg)[0] == decode_MQTT_message(expected_msg)[0])
    payload_check = (decode_MQTT_message(output_msg)[1] == decode_MQTT_message(expected_msg)[1])

    return topic_check and payload_check


def compare_mqtt_msg_list(output_msg_list: List[mqtt.MQTTMessage], expected_msg_list: List[mqtt.MQTTMessage], ignore_order=False):
    if len(output_msg_list) != len(expected_msg_list):
        return False

    if ignore_order:
        for msg1 in output_msg_list:
            found = False
            for msg2 in expected_msg_list:
                if compare_mqtt_msg(msg1, msg2):
                    found = True
                    break
            if not found:
                return False
        return True
    else:
        for i in range(len(output_msg_list)):
            if not compare_mqtt_msg(output_msg_list[i], expected_msg_list[i]):
                return False
        return True
