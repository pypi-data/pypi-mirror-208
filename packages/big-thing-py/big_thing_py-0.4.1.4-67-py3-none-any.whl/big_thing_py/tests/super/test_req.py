from big_thing_py.tests.thing_factory import *
from big_thing_py.tests.conftest import PARAMETRIZE_STRING, compare_mqtt_msg, compare_mqtt_msg_list, MXBasicSuperThing
import pytest


service_list_result_input_level3_with_3_service = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_level3_with_3_service.json')
service_list_result_input_level3_with_1_service = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_level3_with_1_service.json')
service_list_result_input_level3_with_0_service = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_level3_with_0_service.json')
service_list_result_input_level2_with_3_service = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_level2_with_3_service.json')
service_list_result_input_level2_with_1_service = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_level2_with_1_service.json')
service_list_result_input_level2_with_0_service = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_level2_with_0_service.json')
service_list_result_input_level1_with_3_service = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_level1_with_3_service.json')
service_list_result_input_level1_with_1_service = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_level1_with_1_service.json')
service_list_result_input_level1_with_0_service = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_level1_with_0_service.json')


def schedule(super_thing: MXSuperThing):
    ms_schedule_msg = encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                          payload={"scenario": "test", "period": 10000})
    ms_result_schedule_check_msg_list = [encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                             payload={"error": 0, "scenario": "test", "status": "check"})]
    ms_result_schedule_confirm_msg_list = [encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                               payload={"error": 0, "scenario": "test", "status": "confirm"})]

    super_thing._handle_mqtt_message(ms_schedule_msg)

    cnt = len(ms_result_schedule_check_msg_list)
    while cnt:
        sm_schedule_msg = super_thing._publish_queue.get(timeout=0.5)
        if decode_MQTT_message(sm_schedule_msg)[1].get('status', '') == 'check':
            cnt -= 1
        else:
            assert False

    for msg in ms_result_schedule_check_msg_list:
        super_thing._handle_MS_RESULT_SCHEDULE(msg)

    cnt = len(ms_result_schedule_confirm_msg_list)
    while cnt:
        sm_schedule_msg = super_thing._publish_queue.get(timeout=0.5)
        if decode_MQTT_message(sm_schedule_msg)[1].get('status', '') == 'confirm':
            cnt -= 1
        else:
            assert False

    for msg in ms_result_schedule_confirm_msg_list:
        super_thing._handle_MS_RESULT_SCHEDULE(msg)

    time.sleep(0.05)

    while not super_thing._publish_queue.empty():
        super_thing._publish_queue.get()


####################################################################################################################################


def instance_method__test_req_sub_service_name1(self: MXSuperThing) -> int:
    result_list = self.req(sub_service_name='func_no_arg', tag_list=['basic'], arg_list=[],
                           return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)
    return result_list


def instance_method__test_req_sub_service_name2(self: MXSuperThing) -> int:
    result_list = self.req(arg_list=[], tag_list=['basic'],
                           return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)
    return result_list


def instance_method__test_req_sub_service_name3(self: MXSuperThing) -> int:
    result_list = self.req(sub_service_name='', tag_list=['basic'], arg_list=[],
                           return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)
    return result_list


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('req_sub_service_name_0', dict(args=dict(sub_service_name='func_no_arg', tag_list=['basic'], arg_list=[],
                                              return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)),
     True),
    ('req_sub_service_name_1', dict(args=dict(sub_service_name='', tag_list=['basic'], arg_list=[],
                                              return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)),
     MXValueError(r'sub_service_name must be not empty')),
])
def test_req_sub_service_name(test_id: str, input: dict, expected_output: Union[None, Exception]):

    def setup(input: Dict[str, str]) -> Tuple[MXSuperThing, str]:
        super_thing: MXBasicSuperThing = MXBasicSuperThing().setup(avahi_enable=False)
        args: dict = input['args']
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                               payload=service_list_result_input_level3_with_1_service)
        register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing.get_name()),
                                                  payload={'error': 0, 'middleware_name': 'SoPIoT-MW-Level3-0'})
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        return super_thing, args

    def task(super_thing: MXBasicSuperThing, args: dict):
        result = super_thing._check_req_valid(**args)
        return result

    super_thing, args = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            output = task(super_thing, args)
    else:
        output = task(super_thing, args)
        assert output == expected_output

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('req_tag_list_0', dict(args=dict(sub_service_name='func_no_arg', tag_list=['basic'], arg_list=[],
                                      return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)),
     True),
    ('req_tag_list_1', dict(args=dict(sub_service_name='func_no_arg', tag_list=[], arg_list=[],
                                      return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)),
     MXValueError('tag_list must be not empty')),
    ('req_tag_list_2', dict(args=dict(sub_service_name='func_no_arg', tag_list=['basic', ''], arg_list=[],
                                      return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)),
     MXValueError('tag in tag_list must be not empty string')),
])
def test_req_tag_list(test_id: str, input: dict, expected_output: Union[None, Exception]):

    def setup(input: dict):
        super_thing = MXBasicSuperThing()
        args: dict = input['args']
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (MXSuperThing.DEFAULT_NAME),
                                               payload=service_list_result_input_level3_with_1_service)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)
        super_thing._extract_sub_service_request_info()
        return super_thing, args

    def task(super_thing: MXBasicSuperThing, args: dict):
        result = super_thing._check_req_valid(**args)
        return result

    super_thing, args = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            output = task(super_thing, args)
    else:
        output = task(super_thing, args)
        assert output == expected_output


####################################################################################################################################

int_arg__test_req_arg_list = 100
delay__test_req_arg_list = 100


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('req_arg_list_0', dict(sub_service_name='func_with_arg_and_delay', arg_list=[int_arg__test_req_arg_list, delay__test_req_arg_list]),
     True),
    ('req_arg_list_1', dict(sub_service_name='func_with_arg_and_delay', arg_list=[100, delay__test_req_arg_list]),
     True),
    ('req_arg_list_2', dict(sub_service_name='func_with_arg_and_delay', arg_list=[100, 1]),
     True),
    ('req_arg_list_3', dict(sub_service_name='func_with_arg_and_delay', arg_list=[100]),
     False),
    ('req_arg_list_4', dict(sub_service_name='func_with_arg_and_delay', arg_list=[]),
     False),
    ('req_arg_list_5', dict(sub_service_name='func_no_arg', arg_list=[]),
     True),
    ('req_arg_list_6', dict(sub_service_name='func_no_arg', arg_list=[100]),
     False),
])
def test_req_arg_list(test_id: str, input: dict, expected_output: Union[None, Exception]):

    def setup(input: dict):
        super_thing = MXBasicSuperThing()
        sub_service_name = input['sub_service_name']
        arg_list = input['arg_list']
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (MXSuperThing.DEFAULT_NAME),
                                               payload=service_list_result_input_level3_with_1_service)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        super_thing._extract_sub_service_request_info()
        target_sub_service = super_thing._get_sub_service_from_global_service_table(sub_service_name)
        return super_thing, target_sub_service, arg_list

    def task(super_thing: MXBasicSuperThing, target_sub_service: MXFunction, arg_list: list):
        result = super_thing._compare_arg_list(target_sub_service.get_arg_list(), arg_list)
        return result

    super_thing, target_sub_service, arg_list = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            output = task(super_thing, target_sub_service, arg_list)
    else:
        output = task(super_thing, target_sub_service, arg_list)
        assert output == expected_output

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('req_service_type_return_type_0', dict(args=dict(sub_service_name='func_with_arg', tag_list=['basic'], arg_list=[100],
                                                      return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)),
     True),
    ('req_service_type_return_type_1', dict(args=dict(sub_service_name='value_current_time', tag_list=['basic'], arg_list=[],
                                                      return_type=MXType.INTEGER, service_type=MXServiceType.VALUE, range_type=MXRangeType.SINGLE)),
     True),
    ('req_service_type_return_type_2', dict(args=dict(sub_service_name='func_with_arg', tag_list=['basic'], arg_list=[100],
                                                      return_type=MXType.UNDEFINED, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)),
     MXTypeError(r'Invalid return_type: .*')),
    ('req_service_type_return_type_3', dict(args=dict(sub_service_name='func_with_arg', tag_list=['basic'], arg_list=[100],
                                                      return_type=MXType.INTEGER, service_type=MXServiceType.UNDEFINED, range_type=MXRangeType.SINGLE)),
     MXTypeError(r'Invalid service_type: .*')),
    ('req_service_type_return_type_4', dict(args=dict(sub_service_name='value_current_time', tag_list=['basic'], arg_list=[100],
                                                      return_type=MXType.VOID, service_type=MXServiceType.VALUE, range_type=MXRangeType.SINGLE)),
     MXTypeError('Value service cannot have a return_type of void')),
])
def test_req_service_type_return_type(test_id: str, input: dict, expected_output: Union[None, Exception]):

    def setup(input: Dict[str, str]) -> Tuple[MXSuperThing, str]:
        super_thing: MXBasicSuperThing = MXBasicSuperThing().setup(avahi_enable=False)
        args: dict = input['args']
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                               payload=service_list_result_input_level3_with_1_service)
        register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing.get_name()),
                                                  payload={'error': 0, 'middleware_name': 'SoPIoT-MW-Level3-0'})
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        return super_thing, args

    def task(super_thing: MXBasicSuperThing, args: dict):
        result = super_thing._check_req_valid(**args)
        return result

    super_thing, args = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            output = task(super_thing, args)
    else:
        output = task(super_thing, args)
        assert output == expected_output


####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('req_range_type_0', dict(args=dict(sub_service_name='func_no_arg', tag_list=['basic'], arg_list=[],
                                        return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.SINGLE)),
     True),
    ('req_range_type_1', dict(args=dict(sub_service_name='func_no_arg', tag_list=['basic'], arg_list=[],
                                        return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.ALL)),
     True),
    ('req_range_type_2', dict(args=dict(sub_service_name='func_no_arg', tag_list=['basic'], arg_list=[],
                                        return_type=MXType.INTEGER, service_type=MXServiceType.FUNCTION, range_type=MXRangeType.UNDEFINED)),
     MXTypeError(r'Invalid range_type: .*')),
])
def test_req_range_type(test_id: str, input: dict, expected_output: Union[None, Exception]):

    def setup(input: Dict[str, str]) -> Tuple[MXSuperThing, str]:
        super_thing: MXBasicSuperThing = MXBasicSuperThing().setup(avahi_enable=False)
        args: dict = input['args']
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                               payload=service_list_result_input_level3_with_1_service)
        register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing.get_name()),
                                                  payload={'error': 0, 'middleware_name': 'SoPIoT-MW-Level3-0'})
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        return super_thing, args

    def task(super_thing: MXBasicSuperThing, args: dict):
        result = super_thing._check_req_valid(**args)
        return result

    super_thing, args = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            output = task(super_thing, args)
    else:
        output = task(super_thing, args)
        assert output == expected_output

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('req_callable_0', dict(sub_service_name='func_no_arg', return_type=MXType.INTEGER),
     True),
    ('req_callable_1', dict(sub_service_name='not_exist_function', return_type=MXType.INTEGER),
     False),
    ('req_callable_2', dict(sub_service_name='func_no_arg',  return_type=MXType.VOID),
     False),
])
def test_req_callable(test_id: str, input: dict, expected_output: Union[None, Exception]):

    def setup(input: Dict[str, str]) -> Tuple[MXSuperThing, str]:
        super_thing: MXBasicSuperThing = MXBasicSuperThing().setup(avahi_enable=False)
        sub_service_name: str = input['sub_service_name']
        return_type: MXType = input['return_type']
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                               payload=service_list_result_input_level3_with_1_service)
        register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing.get_name()),
                                                  payload={'error': 0, 'middleware_name': 'SoPIoT-MW-Level3-0'})
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        return super_thing, sub_service_name, return_type

    def task(super_thing: MXBasicSuperThing, sub_service_name: str, return_type: MXType):
        result = super_thing._check_sub_service_callable(sub_service_name, return_type)
        return result

    super_thing, sub_service_name, return_type = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            output = task(super_thing, sub_service_name, return_type)
    else:
        output = task(super_thing, sub_service_name, return_type)
        assert output == expected_output


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
