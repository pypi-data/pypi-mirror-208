from big_thing_py.tests.thing_factory import *
from big_thing_py.tests.conftest import PARAMETRIZE_STRING_OLD, PARAMETRIZE_STRING, compare_mqtt_msg, compare_mqtt_msg_list, MXBasicSuperThing
import pytest
import pickle


def global_function() -> int:
    return 1


####################################################################################################################################


class MXSuperThing_TestInitSuperService(MXSuperThing):
    def __init__(self, name: str = MXSuperThing.DEFAULT_NAME, service_list: List[MXService] = [], alive_cycle: float = 60, is_super: bool = True, is_parallel: bool = True,
                 ip: str = '127.0.0.1', port: int = 1883, ssl_ca_path: str = '', ssl_enable: bool = False,
                 log_name: str = None, log_enable: bool = True, log_mode: MXPrintMode = MXPrintMode.ABBR,
                 append_mac_address: bool = True,
                 refresh_cycle: float = 30,
                 super_service_params_list: List[str] = []):

        value_list = []
        function_list = []
        for super_service_params in super_service_params_list:
            super_service = eval(f'MXSuperFunction({super_service_params})')
            function_list.append(super_service)

        service_list = value_list + function_list
        super().__init__(name, service_list, alive_cycle, is_super, is_parallel, ip, port,
                         ssl_ca_path, ssl_enable, log_name, log_enable, log_mode, append_mac_address, refresh_cycle)

####################################################################################################################################


def instance_method__test_init_super_service1(self: MXSuperThing) -> int:
    return 1


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('init_super_service_0', dict(bind_method=instance_method__test_init_super_service1,
                                  super_service_params_list=['func=self.instance_method__test_init_super_service1, return_type=MXType.INTEGER, tag_list=[MXTag(\'tag1\'), MXTag(\'tag2\'), MXTag(\'tag3\')], arg_list=[], timeout=300, exec_time=1, energy=100']),
     b'\x80\x04\x95\xc1\x03\x00\x00\x00\x00\x00\x00\x8c0big_thing_py.tests.super.test_init_super_service\x94\x8c!MXSuperThing_TestInitSuperService\x94\x93\x94)\x81\x94}\x94(\x8c\x15_global_service_table\x94}\x94(\x8c\x06values\x94]\x94\x8c\tfunctions\x94]\x94u\x8c _SUPER_SERVICE_REQUEST_KEY_TABLE\x94}\x94\x8c\x05_name\x94\x8c\x13default_super_thing\x94\x8c\r_service_list\x94]\x94\x8c!big_thing_py.super.super_function\x94\x8c\x0fMXSuperFunction\x94\x93\x94)\x81\x94}\x94(h\r\x8c)instance_method__test_init_super_service1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\rh\x0esbh\x1b)\x81\x94}\x94h\r\x8c\x04tag1\x94sbh\x1b)\x81\x94}\x94h\r\x8c\x04tag2\x94sbh\x1b)\x81\x94}\x94h\r\x8c\x04tag3\x94sbe\x8c\x07_energy\x94Kd\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x0e\x8c\x10_middleware_name\x94h)\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94\x8c\n_exec_time\x94K\x01\x8c\x08_timeout\x94M,\x01\x8c\x0b_range_type\x94h-\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94\x8c\x19_sub_service_request_list\x94]\x94\x8c\x0b_is_scanned\x94\x89\x8c\x1b_temporary_scheduling_table\x94}\x94\x8c\x0e_mapping_table\x94}\x94uba\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x88\x8c\x0c_is_parallel\x94\x88h+N\x8c\x0e_function_list\x94]\x94h\x14a\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94h)\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88\x8c\x0e_refresh_cycle\x94K\x1eub.'),
    ('init_super_service_1', dict(bind_method=None,
                                  super_service_params_list=['func=global_function, return_type=MXType.INTEGER, tag_list=[MXTag(\'tag1\'), MXTag(\'tag2\'), MXTag(\'tag3\')], arg_list=[], timeout=300, exec_time=1, energy=100']),
     MXTypeError('self._func must be a instance method')),
])
def test_init_super_service(test_id: str, input: dict, expected_output: Union[None, Exception]):

    def setup(input):
        bind_method: List[Callable] = input['bind_method']
        super_service_params_list: List[str] = input['super_service_params_list']

        setattr(MXSuperThing_TestInitSuperService, bind_method.__name__, bind_method) if bind_method else None
        return super_service_params_list

    def task(super_service_params_list):
        super_thing = MXSuperThing_TestInitSuperService(super_service_params_list=super_service_params_list)
        return super_thing

    super_service_params_list = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            output = task(super_service_params_list)
    else:
        output = task(super_service_params_list)
        MXLOG_DEBUG(f'\n\n<test_id>\n{test_id}\n<output>\n{pickle.dumps(output)}), ', 'yellow')
        assert pickle.dumps(output) == expected_output

####################################################################################################################################


def instance_method__test_generate_sub_service_request_info1(self: MXSuperThing) -> int:
    return 1


def instance_method__test_generate_sub_service_request_info2(self: MXSuperThing, int_arg: int) -> int:
    result_list = self.req(sub_service_name='func_no_arg', arg_list=[], tag_list=['basic'],
                           return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION)
    result_list = self.req(sub_service_name='func_with_arg', arg_list=[int_arg], tag_list=['basic'],
                           return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION)
    result_value = sum(result['return_value'] for result in result_list) / \
        len(result_list) if len(result_list) > 0 else 0
    result_list = self.req(sub_service_name='func_with_arg', arg_list=[result_value], tag_list=['basic'],
                           return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION)
    self.req(sub_service_name='value_current_time', arg_list=[], tag_list=['basic'],
             return_type=MXType.DOUBLE, service_type=MXServiceType.VALUE, range_type=MXRangeType.ALL)
    return 1


@pytest.mark.parametrize(PARAMETRIZE_STRING_OLD, [
    ('sub_service_request_info_gen_0', dict(bind_method_list=[instance_method__test_generate_sub_service_request_info1],
                                            super_service_params_list=['func=self.instance_method__test_generate_sub_service_request_info1, return_type=MXType.INTEGER, tag_list=[MXTag(\'super1\')], arg_list=[], timeout=300, exec_time=1, energy=100']),
     [[]], None),
    ('sub_service_request_info_gen_1', dict(bind_method_list=[instance_method__test_generate_sub_service_request_info2],
                                            super_service_params_list=['func=self.instance_method__test_generate_sub_service_request_info2, return_type=MXType.INTEGER, tag_list=[MXTag(\'super2\')], arg_list=[MXArgument(name=\'int_arg\', type=MXType.INTEGER, bound=(0, 10000))], timeout=300, exec_time=1, energy=100']),
     [[MXSubServiceRequest(sub_service_type=MXFunction(name='func_no_arg',
                                                       func=dummy_func([]),
                                                       return_type=MXType.INTEGER,
                                                       arg_list=[],
                                                       tag_list=[MXTag('basic')]),
                           sub_service_request_order=0),
       MXSubServiceRequest(sub_service_type=MXFunction(name='func_with_arg',
                                                       func=dummy_func(['int_arg']),
                                                       return_type=MXType.INTEGER,
                                                       arg_list=[MXArgument(name='int_arg', type=MXType.INTEGER, bound=(0, 10000))],
                                                       tag_list=[MXTag('basic')]),
                           sub_service_request_order=1),
       MXSubServiceRequest(sub_service_type=MXFunction(name='func_with_arg',
                                                       func=dummy_func(['int_arg']),
                                                       return_type=MXType.INTEGER,
                                                       arg_list=[MXArgument(name='int_arg', type=MXType.INTEGER, bound=(0, 10000))],
                                                       tag_list=[MXTag('basic')]),
                           sub_service_request_order=2),
       MXSubServiceRequest(sub_service_type=MXFunction(name='value_current_time',
                                                       func=dummy_func([]),
                                                       return_type=MXType.DOUBLE,
                                                       arg_list=[],
                                                       tag_list=[MXTag('basic')],
                                                       range_type=MXRangeType.ALL),
                           sub_service_request_order=3)]], None),
    ('sub_service_request_info_gen_2', dict(bind_method_list=[instance_method__test_generate_sub_service_request_info1, instance_method__test_generate_sub_service_request_info2],
                                            super_service_params_list=['func=self.instance_method__test_generate_sub_service_request_info1, return_type=MXType.INTEGER, tag_list=[MXTag(\'super1\')], arg_list=[], timeout=300, exec_time=1, energy=100',
                                                                       'func=self.instance_method__test_generate_sub_service_request_info2, return_type=MXType.INTEGER, tag_list=[MXTag(\'super2\')], arg_list=[MXArgument(name=\'int_arg\', type=MXType.INTEGER, bound=(0, 10000))], timeout=300, exec_time=1, energy=100']),
     [[], [MXSubServiceRequest(sub_service_type=MXFunction(name='func_no_arg',
                                                           func=dummy_func([]),
                                                           return_type=MXType.INTEGER,
                                                           arg_list=[],
                                                           tag_list=[MXTag('basic')]),
                               sub_service_request_order=0),
           MXSubServiceRequest(sub_service_type=MXFunction(name='func_with_arg',
                                                           func=dummy_func(['int_arg']),
                                                           return_type=MXType.INTEGER,
                                                           arg_list=[MXArgument(name='int_arg', type=MXType.INTEGER, bound=(0, 10000))],
                                                           tag_list=[MXTag('basic')]),
                               sub_service_request_order=1),
           MXSubServiceRequest(sub_service_type=MXFunction(name='func_with_arg',
                                                           func=dummy_func(['int_arg']),
                                                           return_type=MXType.INTEGER,
                                                           arg_list=[MXArgument(name='int_arg', type=MXType.INTEGER, bound=(0, 10000))],
                                                           tag_list=[MXTag('basic')]),
                               sub_service_request_order=2),
           MXSubServiceRequest(sub_service_type=MXFunction(name='value_current_time',
                                                           func=dummy_func([]),
                                                           return_type=MXType.DOUBLE,
                                                           arg_list=[],
                                                           tag_list=[MXTag('basic')],
                                                           range_type=MXRangeType.ALL),
                               sub_service_request_order=3)]], None),
])
def test_generate_sub_service_request_info(test_id: str, input: dict, expected_output, expected_exception_message: str):
    bind_method_list: List[Callable] = input['bind_method_list']
    super_service_params_list: List[str] = input['super_service_params_list']

    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=expected_exception_message):
            output = MXSuperThing_TestInitSuperService(super_service_params_list=super_service_params_list)
            output._extract_sub_service_request_info()
    else:
        for bind_method in bind_method_list:
            setattr(MXSuperThing_TestInitSuperService, bind_method.__name__, bind_method)
        output = MXSuperThing_TestInitSuperService(super_service_params_list=super_service_params_list)
        output._extract_sub_service_request_info()
        for func, expected_sub_service_request_list in zip(output.get_function_list(), expected_output):
            assert func._sub_service_request_list == expected_sub_service_request_list

####################################################################################################################################


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
