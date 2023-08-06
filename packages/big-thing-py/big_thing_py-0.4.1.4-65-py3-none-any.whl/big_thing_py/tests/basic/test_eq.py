from big_thing_py.tests.thing_factory import *
import pytest


def test_argument_eq():
    raw_arg = MXArgument(name='arg1', type=MXType.INTEGER,
                         bound=(0, 100))
    same_arg = MXArgument(name='arg1', type=MXType.INTEGER,
                          bound=(0, 100))
    diff_name_arg = MXArgument(name='arg2', type=MXType.INTEGER,
                               bound=(0, 100))
    diff_bound_arg = MXArgument(name='arg1', type=MXType.INTEGER,
                                bound=(0, 110))
    diff_type_arg = MXArgument(name='arg1', type=MXType.BOOL,
                               bound=(0, 110))

    assert raw_arg == same_arg
    assert raw_arg != diff_name_arg
    assert raw_arg != diff_bound_arg
    assert raw_arg != diff_type_arg

####################################################################################################################################


def test_function_eq():
    thing_name = 'test_thing'
    middleware_name = 'test_thing'
    desc = 'test_desc'
    arg1 = MXArgument(name='arg1', type=MXType.INTEGER,
                      bound=(0, 100))
    arg2 = MXArgument(name='arg2', type=MXType.BOOL,
                      bound=(0, 100))
    arg3 = MXArgument(name='arg3', type=MXType.STRING,
                      bound=(0, 100))
    tag1 = MXTag(name='tag1')
    tag2 = MXTag(name='tag2')
    tag3 = MXTag(name='tag3')

    raw_function = MXFunction(name='function1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_with_argument_with_return_1, energy=100,
                              arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                        MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                        MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                        MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    same_function = MXFunction(name='function1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_with_argument_with_return_1, energy=100,
                               arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                         MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                         MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                         MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    diff_desc_function = MXFunction(name='function1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc='diff_test_desc', func=func_with_argument_with_return_1, energy=100,
                                    arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                              MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                              MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                              MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    diff_name_function = MXFunction(name='function2', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_with_argument_with_return_1, energy=100,
                                    arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                              MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                              MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                              MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    diff_thing_name_function = MXFunction(name='function1', thing_name='diff_test_thing', middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_with_argument_with_return_1, energy=100,
                                          arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                    MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                    MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                    MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    diff_middleware_name_function = MXFunction(name='function1', thing_name=thing_name, middleware_name='diff_test_middleware', tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_with_argument_with_return_1, energy=100,
                                               arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                         MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                         MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                         MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    diff_tag_list_function1 = MXFunction(name='function1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag2')], desc=desc, func=func_with_argument_with_return_1, energy=100,
                                         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                   MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                   MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    diff_tag_list_function2 = MXFunction(name='function1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag3')], desc=desc, func=func_with_argument_with_return_1, energy=100,
                                         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                   MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                   MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    diff_tag_list_function3 = MXFunction(name='function1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag(name='tag3')], desc=desc, func=func_with_argument_with_return_1, energy=100,
                                         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                   MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                   MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    diff_func_function = MXFunction(name='function1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_with_argument_with_return_2, energy=100,
                                    arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                              MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                              MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                              MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    diff_energy_function = MXFunction(name='function1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_with_argument_with_return_1, energy=110,
                                      arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    diff_return_type_function = MXFunction(name='function1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_with_argument_with_return_1, energy=100,
                                           arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                     MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                     MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                     MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.BOOL, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    diff_exec_time_function = MXFunction(name='function1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_with_argument_with_return_1, energy=100,
                                         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                   MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                   MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=11, timeout=10, range_type=MXRangeType.SINGLE)
    diff_timeout_function = MXFunction(name='function1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_with_argument_with_return_1, energy=100,
                                       arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                 MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                 MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                 MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=11, range_type=MXRangeType.SINGLE)
    diff_range_type_function = MXFunction(name='function1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_with_argument_with_return_1, energy=100,
                                          arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                    MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                    MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                    MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.ALL)

    assert raw_function == same_function
    assert raw_function == diff_desc_function
    assert raw_function != diff_name_function
    assert raw_function != diff_thing_name_function
    assert raw_function != diff_middleware_name_function
    assert raw_function != diff_tag_list_function1
    assert raw_function != diff_tag_list_function2
    assert raw_function != diff_tag_list_function3
    assert raw_function != diff_func_function
    assert raw_function != diff_energy_function
    assert raw_function != diff_return_type_function
    assert raw_function != diff_exec_time_function
    assert raw_function != diff_timeout_function
    assert raw_function != diff_range_type_function

####################################################################################################################################


def test_thing_eq():
    desc = 'test_desc'

    tag1 = MXTag(name='tag1')
    tag2 = MXTag(name='tag2')
    tag3 = MXTag(name='tag3')
    int_arg = MXArgument(name='int_arg', type=MXType.INTEGER, bound=(0, 100))
    float_arg = MXArgument(
        name='float_arg', type=MXType.DOUBLE, bound=(0, 100.0))
    str_arg = MXArgument(name='str_arg', type=MXType.STRING, bound=(0, 100))
    bool_arg = MXArgument(name='bool_arg', type=MXType.BOOL, bound=(0, 2))

    value1 = MXValue(name='value1', tag_list=[tag1], desc=desc, func=func_no_argument_with_return_1, energy=100,
                     type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)
    value2 = MXValue(name='value2', tag_list=[tag2], desc=desc, func=func_no_argument_with_return_2, energy=100,
                     type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)
    value3 = MXValue(name='value3', tag_list=[tag3], desc=desc, func=func_no_argument_with_return_3, energy=100,
                     type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)

    function1 = MXFunction(name='function1', tag_list=[tag1], desc=desc, func=func_with_argument_with_return_1, energy=100,
                           arg_list=[int_arg, float_arg, str_arg, bool_arg], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    function2 = MXFunction(name='function2', tag_list=[tag2], desc=desc, func=func_with_argument_with_return_2, energy=100,
                           arg_list=[int_arg, float_arg, str_arg, bool_arg], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)
    function3 = MXFunction(name='function3', tag_list=[tag3], desc=desc, func=func_with_argument_with_return_3, energy=100,
                           arg_list=[int_arg, float_arg, str_arg, bool_arg], return_type=MXType.INTEGER, exec_time=10, timeout=10, range_type=MXRangeType.SINGLE)

    raw_thing = MXThing(name='thing1', service_list=[value1, value2] + [function1, function2],
                        alive_cycle=60, is_super=False, is_parallel=True)
    same_thing = MXThing(name='thing1', service_list=[value1, value2] + [function1, function2],
                         alive_cycle=60, is_super=False, is_parallel=True)
    diff_name_thing = MXThing(name='thing2', service_list=[value1, value2] + [function1, function2],
                              alive_cycle=60, is_super=False, is_parallel=True)
    diff_value_list_thing1 = MXThing(name='thing1', service_list=[value3] + [function1, function2],
                                     alive_cycle=60, is_super=False, is_parallel=True)
    diff_value_list_thing2 = MXThing(name='thing1', service_list=[value1] + [function1, function2],
                                     alive_cycle=60, is_super=False, is_parallel=True)
    diff_value_list_thing3 = MXThing(name='thing1', service_list=[value1, value2, value3] + [function1, function2],
                                     alive_cycle=60, is_super=False, is_parallel=True)
    diff_function_list_thing1 = MXThing(name='thing1', service_list=[value1, value2] + [function3],
                                        alive_cycle=60, is_super=False, is_parallel=True)
    diff_function_list_thing2 = MXThing(name='thing1', service_list=[value1, value2] + [function1],
                                        alive_cycle=60, is_super=False, is_parallel=True)
    diff_function_list_thing3 = MXThing(name='thing1', service_list=[value1, value2] + [function1, function2, function3],
                                        alive_cycle=60, is_super=False, is_parallel=True)
    diff_alive_cycle_thing = MXThing(name='thing1', service_list=[value1, value2] + [function1, function2],
                                     alive_cycle=120, is_super=False, is_parallel=True)
    diff_is_super_thing = MXThing(name='thing1', service_list=[value1, value2] + [function1, function2],
                                  alive_cycle=60, is_super=True, is_parallel=True)
    diff_is_parallel_thing = MXThing(name='thing1', service_list=[value1, value2] + [function1, function2],
                                     alive_cycle=60, is_super=False, is_parallel=False)

    assert raw_thing == same_thing
    assert raw_thing != diff_name_thing
    assert raw_thing != diff_value_list_thing1
    assert raw_thing != diff_value_list_thing2
    assert raw_thing != diff_value_list_thing3
    assert raw_thing != diff_function_list_thing1
    assert raw_thing != diff_function_list_thing2
    assert raw_thing != diff_function_list_thing3
    assert raw_thing != diff_alive_cycle_thing
    assert raw_thing != diff_is_super_thing
    assert raw_thing != diff_is_parallel_thing

####################################################################################################################################


def test_value_eq():
    thing_name = 'test_thing'
    middleware_name = 'test_thing'
    desc = 'test_desc'
    tag1 = MXTag(name='tag1')
    tag2 = MXTag(name='tag2')
    tag3 = MXTag(name='tag3')

    raw_value = MXValue(name='value1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_no_argument_with_return_1, energy=100,
                        type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)
    same_value = MXValue(name='value1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_no_argument_with_return_1, energy=100,
                         type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)
    diff_desc_value = MXValue(name='value1', thing_name='diff_test_thing', middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc='diff_test_desc', func=func_no_argument_with_return_1, energy=100,
                              type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)
    diff_thing_name_value = MXValue(name='value1', thing_name='diff_test_thing', middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_no_argument_with_return_1, energy=100,
                                    type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)
    diff_middleware_name_value = MXValue(name='value1', thing_name=thing_name, middleware_name='diff_test_middleware', tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_no_argument_with_return_1, energy=100,
                                         type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)
    diff_tag_list_value1 = MXValue(name='value1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag3')], desc=desc, func=func_no_argument_with_return_1, energy=100,
                                   type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)
    diff_tag_list_value2 = MXValue(name='value1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag3')], desc=desc, func=func_no_argument_with_return_1, energy=100,
                                   type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)
    diff_tag_list_value3 = MXValue(name='value1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')], desc=desc, func=func_no_argument_with_return_1, energy=100,
                                   type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)
    diff_func_value = MXValue(name='value1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_no_argument_with_return_2, energy=100,
                              type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)
    diff_energy_value = MXValue(name='value1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_no_argument_with_return_1, energy=110,
                                type=MXType.INTEGER, bound=(0, 100), format='', cycle=10)
    diff_type_value = MXValue(name='value1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_no_argument_with_return_1, energy=100,
                              type=MXType.BOOL, bound=(0, 100), format='', cycle=10)
    diff_bound_value = MXValue(name='value1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_no_argument_with_return_1, energy=100,
                               type=MXType.INTEGER, bound=(0, 110), format='', cycle=10)
    diff_format_value = MXValue(name='value1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_no_argument_with_return_1, energy=100,
                                type=MXType.INTEGER, bound=(0, 100), format='diff_format', cycle=10)
    diff_cycle_value = MXValue(name='value1', thing_name=thing_name, middleware_name=middleware_name, tag_list=[MXTag('tag1'), MXTag('tag2')], desc=desc, func=func_no_argument_with_return_1, energy=100,
                               type=MXType.INTEGER, bound=(0, 100), format='', cycle=11)

    assert raw_value == same_value
    assert raw_value == same_value
    assert raw_value != diff_desc_value
    assert raw_value != diff_thing_name_value
    assert raw_value != diff_middleware_name_value
    assert raw_value != diff_tag_list_value1
    assert raw_value != diff_tag_list_value2
    assert raw_value != diff_tag_list_value3
    assert raw_value != diff_func_value
    assert raw_value != diff_energy_value
    assert raw_value != diff_type_value
    assert raw_value != diff_bound_value
    assert raw_value != diff_format_value
    assert raw_value != diff_cycle_value

####################################################################################################################################


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
