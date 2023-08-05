from big_thing_py.tests.thing_factory import *
from big_thing_py.tests.conftest import PARAMETRIZE_STRING_OLD, compare_mqtt_msg, compare_mqtt_msg_list, MXBasicSuperThing
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


####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING_OLD, [
    ('schedule_topic_0', dict(input_topic=f'MS/SCHEDULE/super_multiple_sub_service_request_with_fixed_argument2/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0'),
     True, None),
    ('schedule_topic_1', dict(input_topic=f'M3/SCHEDULE/super_multiple_sub_service_request_with_fixed_argument2/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0'),
     False, None),
    ('schedule_topic_2', dict(input_topic=f'MS/SCH3DULE/super_multiple_sub_service_request_with_fixed_argument2/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0'),
     False, None),
    ('schedule_topic_3', dict(input_topic=f'MS/SCHEDULE/not_exist_super_service/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0'),
     False, None),
    ('schedule_topic_4', dict(input_topic=f'MS/SCHEDULE/super_multiple_sub_service_request_with_fixed_argument2/not_exist_super_thing/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0'),
     False, None),
    ('schedule_topic_5', dict(input_topic=f'MS/SCHEDULE/super_multiple_sub_service_request_with_fixed_argument2/super_thing_1/not_exist_super_middleware/SoPIoT-MW-Level1-0'),
     False, None),
])
@pytest.mark.usefixtures('run_mosquitto')
def test_handle_schedule_topic(test_id: str, input: dict[str, str], expected_output: Union[bool, Exception], expected_exception_message: str):
    input_topic: str = input['input_topic']
    input_payload: str = {"scenario": "test", "period": 10000}
    super_thing = MXBasicSuperThing(name='super_thing_1', append_mac_address=False)
    super_thing.setup(avahi_enable=False)

    msg = encode_MQTT_message(topic=input_topic, payload=input_payload)
    service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                           payload=service_list_result_input_level3_with_1_service)
    register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing.get_name()),
                                              payload={'error': 0, 'middleware_name': 'SoPIoT-MW-Level3-0'})
    super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
    super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=expected_exception_message):
            super_thing._handle_mqtt_message(msg)
    else:
        output = super_thing._handle_mqtt_message(msg)
        assert output == expected_output


####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING_OLD, [
    ('schedule_payload_0', dict(input_payload={"scenario": "test", "period": 10000}),
     True, None),
    ('schedule_payload_1', dict(input_payload={"scenar": "test", "period": 10000}),
     KeyError(), r'.*'),
    ('schedule_payload_2', dict(input_payload={"scenario": 100, "period": 10000}),
     False, None),
    ('schedule_payload_3', dict(input_payload={"scenario": "test", "peri": 10000}),
     KeyError(), r'.*'),
    ('schedule_payload_4', dict(input_payload={"scenario": "test", "period": "10000"}),
     False, None),
])
@pytest.mark.usefixtures('run_mosquitto')
def test_handle_schedule_payload(test_id: str, input: dict, expected_output: Union[None, Exception], expected_exception_message: str):
    super_service_name = 'super_multiple_sub_service_request_with_fixed_argument2'
    input_topic: str = f'MS/SCHEDULE/{super_service_name}/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0'
    input_payload: str = input['input_payload']
    schedule_msg = encode_MQTT_message(topic=input_topic, payload=input_payload)

    # TODO: move to preprocess (fixture? setup?)
    def setup_super_thing():
        super_thing = MXBasicSuperThing(name='super_thing_1', append_mac_address=False)
        super_thing.setup(avahi_enable=False)

        # simulate registeration
        register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing.get_name()),
                                                  payload={'error': 0, 'middleware_name': 'SoPIoT-MW-Level3-0'})
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)

        # simulate service list initialization
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                               payload=service_list_result_input_level3_with_1_service)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        return super_thing

    def task(super_thing: MXSuperThing, msg):
        result = super_thing._handle_MS_SCHEDULE(msg)
        return result

    super_thing = setup_super_thing()

    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=expected_exception_message):
            task(super_thing, schedule_msg)
    else:
        output = task(super_thing, schedule_msg)
        assert output == expected_output


####################################################################################################################################

@pytest.mark.parametrize(PARAMETRIZE_STRING_OLD, [
    ('schedule_check_confirm_0', dict(service_list=service_list_result_input_level3_with_0_service,
                                      ms_schedule_topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                      ms_schedule_payload={"scenario": "test", "period": 10000},
                                      ms_result_schedule_check_topic_list=[],
                                      ms_result_schedule_check_payload_list=[],
                                      ms_result_schedule_confirm_topic_list=[],
                                      ms_result_schedule_confirm_payload_list=[]),
     dict(sm_schedule_check_topic_list=[],
          sm_schedule_check_payload_list=[],
          sm_schedule_confirm_topic_list=[],
          sm_schedule_confirm_payload_list=[],
          sm_result_schedule_topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
          sm_result_schedule_payload={"error": -1, "scenario": "test"}), None),
    ('schedule_check_confirm_1', dict(service_list=service_list_result_input_level3_with_1_service,
                                      ms_schedule_topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                      ms_schedule_payload={"scenario": "test", "period": 10000},
                                      ms_result_schedule_check_topic_list=[
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
                                      ms_result_schedule_check_payload_list=[
                                          {"error": 0, "scenario": "test", "status": "check"}],
                                      ms_result_schedule_confirm_topic_list=[
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
                                      ms_result_schedule_confirm_payload_list=[
                                          {"error": 0, "scenario": "test", "status": "confirm"}]),
     dict(sm_schedule_check_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
        sm_schedule_check_payload_list=[
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}],
        sm_schedule_confirm_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
        sm_schedule_confirm_payload_list=[
         {"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}],
        sm_result_schedule_topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
        sm_result_schedule_payload={"error": 0, "scenario": "test"}), None),
    ('schedule_check_confirm_2', dict(service_list=service_list_result_input_level3_with_3_service,
                                      ms_schedule_topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                      ms_schedule_payload={"scenario": "test", "period": 10000},
                                      ms_result_schedule_check_topic_list=[
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
                                      ms_result_schedule_check_payload_list=[
                                          {"error": 0, "scenario": "test", "status": "check"},
                                          {"error": 0, "scenario": "test", "status": "check"},
                                          {"error": 0, "scenario": "test", "status": "check"}],
                                      ms_result_schedule_confirm_topic_list=[
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
                                      ms_result_schedule_confirm_payload_list=[
                                          {"error": 0, "scenario": "test", "status": "confirm"},
                                          {"error": 0, "scenario": "test", "status": "confirm"},
                                          {"error": 0, "scenario": "test", "status": "confirm"}]),
     dict(sm_schedule_check_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
        sm_schedule_check_payload_list=[
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}],
        sm_schedule_confirm_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
        sm_schedule_confirm_payload_list=[
         {"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}],
        sm_result_schedule_topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
        sm_result_schedule_payload={"error": 0, "scenario": "test"}), None),
    ('schedule_check_confirm_3', dict(service_list=service_list_result_input_level3_with_0_service,
                                      ms_schedule_topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                      ms_schedule_payload={"scenario": "test", "period": 10000},
                                      ms_result_schedule_check_topic_list=[],
                                      ms_result_schedule_check_payload_list=[],
                                      ms_result_schedule_confirm_topic_list=[],
                                      ms_result_schedule_confirm_payload_list=[]),
     dict(sm_schedule_check_topic_list=[],
          sm_schedule_check_payload_list=[],
          sm_schedule_confirm_topic_list=[],
          sm_schedule_confirm_payload_list=[],
          sm_result_schedule_topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
          sm_result_schedule_payload={"error": -1, "scenario": "test"}), None),
    ('schedule_check_confirm_4', dict(service_list=service_list_result_input_level3_with_1_service,
                                      ms_schedule_topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                      ms_schedule_payload={"scenario": "test", "period": 10000},
                                      ms_result_schedule_check_topic_list=[
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0'],
                                      ms_result_schedule_check_payload_list=[
                                          {"error": 0, "scenario": "test", "status": "check"}],
                                      ms_result_schedule_confirm_topic_list=[
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0'],
                                      ms_result_schedule_confirm_payload_list=[
                                          {"error": 0, "scenario": "test", "status": "confirm"}]),
     dict(sm_schedule_check_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0'],
        sm_schedule_check_payload_list=[
         {"period": 10000, "range": "single", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}],
        sm_schedule_confirm_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0'],
        sm_schedule_confirm_payload_list=[
         {"period": 10000, "range": "single", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}],
        sm_result_schedule_topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
        sm_result_schedule_payload={"error": 0, "scenario": "test"}), None),
    ('schedule_check_confirm_5', dict(service_list=service_list_result_input_level3_with_3_service,
                                      ms_schedule_topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                      ms_schedule_payload={"scenario": "test", "period": 10000},
                                      ms_result_schedule_check_topic_list=[
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0'],
                                      ms_result_schedule_check_payload_list=[
                                          {"error": 0, "scenario": "test", "status": "check"},
                                          {"error": 0, "scenario": "test", "status": "check"},
                                          {"error": 0, "scenario": "test", "status": "check"}],
                                      ms_result_schedule_confirm_topic_list=[
                                          'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0'],
                                      ms_result_schedule_confirm_payload_list=[
                                          {"error": 0, "scenario": "test", "status": "confirm"}]),
     dict(sm_schedule_check_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0'],
        sm_schedule_check_payload_list=[
         {"period": 10000, "range": "single", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "single", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "single", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}],
        sm_schedule_confirm_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0'],
        sm_schedule_confirm_payload_list=[
         {"period": 10000, "range": "single", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}],
        sm_result_schedule_topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
        sm_result_schedule_payload={"error": 0, "scenario": "test"}), None),
])
@pytest.mark.usefixtures('run_mosquitto')
# @pytest.mark.skip(reason="not implemented yet")
def test_schedule_check_confirm(test_id: str, input: Dict[str, Union[str, List[str], List[dict]]], expected_output: Union[None, Exception], expected_exception_message: str):
    super_thing_name = 'super_thing_1'
    super_service_name = input['ms_schedule_topic'].split('/')[2]
    ms_schedule_msg = encode_MQTT_message(topic=input['ms_schedule_topic'],
                                          payload=input['ms_schedule_payload'])
    ms_result_schedule_check_msg_list = [encode_MQTT_message(topic=topic, payload=payload) for
                                         topic, payload in zip(input['ms_result_schedule_check_topic_list'], input['ms_result_schedule_check_payload_list'])]
    ms_result_schedule_confirm_msg_list = [encode_MQTT_message(topic=topic, payload=payload) for
                                           topic, payload in zip(input['ms_result_schedule_confirm_topic_list'], input['ms_result_schedule_confirm_payload_list'])]

    expected_sm_schedule_check_msg_list = [encode_MQTT_message(topic=topic, payload=payload) for
                                           topic, payload in zip(expected_output['sm_schedule_check_topic_list'], expected_output['sm_schedule_check_payload_list'])]
    expected_sm_schedule_confirm_msg_list = [encode_MQTT_message(topic=topic, payload=payload) for
                                             topic, payload in zip(expected_output['sm_schedule_confirm_topic_list'], expected_output['sm_schedule_confirm_payload_list'])]
    expected_sm_result_schedule_msg = encode_MQTT_message(topic=expected_output['sm_result_schedule_topic'],
                                                          payload=expected_output['sm_result_schedule_payload'])

    service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing_name),
                                           payload=input['service_list'])
    register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing_name),
                                              payload={'error': 0, 'middleware_name': decode_MQTT_message(ms_schedule_msg)[0].split('/')[4]})

    def task(ms_schedule_msg,
             ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list,
             service_list_msg, register_result_msg, super_thing_name, super_service_name):
        output_sm_schedule_check_msg_list: List[mqtt.MQTTMessage] = []
        output_sm_schedule_confirm_msg_list: List[mqtt.MQTTMessage] = []
        output_sm_result_schedule_msg_list: List[mqtt.MQTTMessage] = []

        # TODO: setup으로 빼야 한다.
        super_thing = MXBasicSuperThing(name=super_thing_name, append_mac_address=False)
        super_thing.setup(avahi_enable=False)
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        super_service = super_thing._get_function(super_service_name)
        super_schedule_msg = MXSuperScheduleMessage(ms_schedule_msg)

        # super_schedule_request의 scheduling을 시작하고 running이 True가 될 때까지 기다린다.
        super_service.start_super_schedule_thread(super_schedule_msg, super_thing._global_service_table, timeout=1)
        while not super_service._schedule_running:
            time.sleep(THREAD_TIME_OUT)
            
        time.sleep(0.001)

        # 정상적인 경우의 생성된 요청의 갯수를 가져온다.
        cnt = len(ms_result_schedule_check_msg_list)
        while cnt:
            # 생성된 check 요청 패킷 확인
            sm_schedule_msg = super_thing._publish_queue.get(timeout=0.5)
            if decode_MQTT_message(sm_schedule_msg)[1].get('status', '') == 'check':
                output_sm_schedule_check_msg_list.append(sm_schedule_msg)
                cnt -= 1
            else:
                assert False

        # 정상적인 check 스케줄 결과들을 넣어주고, 잘 처리하는지 확인
        for msg in ms_result_schedule_check_msg_list:
            super_thing._handle_MS_RESULT_SCHEDULE(msg)

        # 정상적인 경우의 생성된 요청의 갯수를 가져온다.
        cnt = len(ms_result_schedule_confirm_msg_list)
        while cnt:
            # 생성된 confirm 요청 패킷 확인
            sm_schedule_msg = super_thing._publish_queue.get(timeout=0.5)
            if decode_MQTT_message(sm_schedule_msg)[1].get('status', '') == 'confirm':
                output_sm_schedule_confirm_msg_list.append(sm_schedule_msg)
                cnt -= 1
            else:
                assert False

        # 정상적인 confirm 스케줄 결과들을 넣어주고, 잘 처리하는지 확인
        for msg in ms_result_schedule_confirm_msg_list:
            super_thing._handle_MS_RESULT_SCHEDULE(msg)

        # running이 False가 될 때까지 기다린다.
        while super_service._schedule_running:
            time.sleep(THREAD_TIME_OUT)
            
        time.sleep(0.001)

        # 최종 scheduling 결과가 오는 것을 모두 받아온다. (비정상적으로 2개의 결과를 보내는 경우를 감지하기 위함)
        while not super_thing._publish_queue.empty():
            output_sm_result_schedule_msg_list.append(super_thing._publish_queue.get())
        for msg in output_sm_result_schedule_msg_list:
            if 'SM/RESULT/SCHEDULE' in decode_MQTT_message(msg)[0]:
                output_sm_result_schedule_msg = msg

        return output_sm_schedule_check_msg_list, output_sm_schedule_confirm_msg_list, output_sm_result_schedule_msg

    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=expected_exception_message):
            task(ms_schedule_msg, ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list,
                 service_list_msg, register_result_msg, super_thing_name, super_service_name)
    else:
        output_sm_schedule_check_msg_list, output_sm_schedule_confirm_msg_list, output_sm_result_schedule_msg = \
            task(ms_schedule_msg, ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list,
                 service_list_msg, register_result_msg, super_thing_name, super_service_name)

        assert compare_mqtt_msg_list(output_sm_schedule_check_msg_list, expected_sm_schedule_check_msg_list)
        assert compare_mqtt_msg_list(output_sm_schedule_confirm_msg_list, expected_sm_schedule_confirm_msg_list)
        assert compare_mqtt_msg(output_sm_result_schedule_msg, expected_sm_result_schedule_msg)

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING_OLD, [
    ('schedule_timeout_0', dict(service_list=service_list_result_input_level3_with_3_service,
                                ms_schedule_topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                ms_schedule_payload={"scenario": "test", "period": 10000},
                                ms_result_schedule_check_topic_list=[
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
                                ms_result_schedule_check_payload_list=[
                                    {"error": 0, "scenario": "test", "status": "check"},
                                    {"error": 0, "scenario": "test", "status": "check"},
                                    {"error": 0, "scenario": "test", "status": "check"}],
                                ms_result_schedule_confirm_topic_list=[
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
                                ms_result_schedule_confirm_payload_list=[
                                    {"error": 0, "scenario": "test", "status": "confirm"},
                                    {"error": 0, "scenario": "test", "status": "confirm"},
                                    {"error": 0, "scenario": "test", "status": "confirm"}],
                                schedule_check_delay=0,
                                schedule_confirm_delay=0),
     dict(sm_schedule_check_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
        sm_schedule_check_payload_list=[
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}],
        sm_schedule_confirm_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
        sm_schedule_confirm_payload_list=[
         {"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}],
        sm_result_schedule_topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
        sm_result_schedule_payload={"error": 0, "scenario": "test"}), None),
    ('schedule_timeout_1', dict(service_list=service_list_result_input_level3_with_3_service,
                                ms_schedule_topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                ms_schedule_payload={"scenario": "test", "period": 10000},
                                ms_result_schedule_check_topic_list=[
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
                                ms_result_schedule_check_payload_list=[
                                    {"error": 0, "scenario": "test", "status": "check"},
                                    {"error": 0, "scenario": "test", "status": "check"},
                                    {"error": 0, "scenario": "test", "status": "check"}],
                                ms_result_schedule_confirm_topic_list=[
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
                                ms_result_schedule_confirm_payload_list=[
                                    {"error": 0, "scenario": "test", "status": "confirm"},
                                    {"error": 0, "scenario": "test", "status": "confirm"},
                                    {"error": 0, "scenario": "test", "status": "confirm"}],
                                schedule_check_delay=1.5,
                                schedule_confirm_delay=0),
     dict(sm_schedule_check_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
        sm_schedule_check_payload_list=[
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}],
        sm_schedule_confirm_topic_list=[],
        sm_schedule_confirm_payload_list=[],
        sm_result_schedule_topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
        sm_result_schedule_payload={"error": -2, "scenario": "test"}), None),
    ('schedule_timeout_2', dict(service_list=service_list_result_input_level3_with_3_service,
                                ms_schedule_topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                ms_schedule_payload={"scenario": "test", "period": 10000},
                                ms_result_schedule_check_topic_list=[
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
                                ms_result_schedule_check_payload_list=[
                                    {"error": 0, "scenario": "test", "status": "check"},
                                    {"error": 0, "scenario": "test", "status": "check"},
                                    {"error": 0, "scenario": "test", "status": "check"}],
                                ms_result_schedule_confirm_topic_list=[
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                    'MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
                                ms_result_schedule_confirm_payload_list=[
                                    {"error": 0, "scenario": "test", "status": "confirm"},
                                    {"error": 0, "scenario": "test", "status": "confirm"},
                                    {"error": 0, "scenario": "test", "status": "confirm"}],
                                schedule_check_delay=0.5,
                                schedule_confirm_delay=1.0),
     dict(sm_schedule_check_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
        sm_schedule_check_payload_list=[
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}],
        sm_schedule_confirm_topic_list=[
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
         'SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0'],
        sm_schedule_confirm_payload_list=[
         {"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]},
         {"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}],
        sm_result_schedule_topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
        sm_result_schedule_payload={"error": -2, "scenario": "test"}), None),
])
def test_schedule_timeout(test_id: str, input: Dict[str, Union[str, List[str], List[dict]]], expected_output: Union[None, Exception], expected_exception_message: str):
    super_thing_name = 'super_thing_1'
    super_service_name = input['ms_schedule_topic'].split('/')[2]
    ms_schedule_msg = encode_MQTT_message(topic=input['ms_schedule_topic'],
                                          payload=input['ms_schedule_payload'])
    ms_result_schedule_check_msg_list = [encode_MQTT_message(topic=topic, payload=payload) for
                                         topic, payload in zip(input['ms_result_schedule_check_topic_list'], input['ms_result_schedule_check_payload_list'])]
    ms_result_schedule_confirm_msg_list = [encode_MQTT_message(topic=topic, payload=payload) for
                                           topic, payload in zip(input['ms_result_schedule_confirm_topic_list'], input['ms_result_schedule_confirm_payload_list'])]

    expected_sm_schedule_check_msg_list = [encode_MQTT_message(topic=topic, payload=payload) for
                                           topic, payload in zip(expected_output['sm_schedule_check_topic_list'], expected_output['sm_schedule_check_payload_list'])]
    expected_sm_schedule_confirm_msg_list = [encode_MQTT_message(topic=topic, payload=payload) for
                                             topic, payload in zip(expected_output['sm_schedule_confirm_topic_list'], expected_output['sm_schedule_confirm_payload_list'])]
    expected_sm_result_schedule_msg = encode_MQTT_message(topic=expected_output['sm_result_schedule_topic'],
                                                          payload=expected_output['sm_result_schedule_payload'])

    service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing_name),
                                           payload=input['service_list'])
    register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing_name),
                                              payload={'error': 0, 'middleware_name': decode_MQTT_message(ms_schedule_msg)[0].split('/')[4]})
    schedule_check_delay = input['schedule_check_delay']
    schedule_confirm_delay = input['schedule_confirm_delay']

    def get_schedule_result_msg(super_thing: MXSuperThing):
        remain_msg_list = []
        while not super_thing._publish_queue.empty():
            remain_msg_list.append(super_thing._publish_queue.get())
        for msg in remain_msg_list:
            if 'SM/RESULT/SCHEDULE' in decode_MQTT_message(msg)[0]:
                return msg

    def task(ms_schedule_msg,
             ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list,
             service_list_msg, register_result_msg, super_thing_name, super_service_name, schedule_check_delay, schedule_confirm_delay):
        output_sm_schedule_check_msg_list: List[mqtt.MQTTMessage] = []
        output_sm_schedule_confirm_msg_list: List[mqtt.MQTTMessage] = []
        output_sm_result_schedule_msg_list: List[mqtt.MQTTMessage] = []

        # TODO: setup으로 빼야 한다.
        super_thing = MXBasicSuperThing(name=super_thing_name, append_mac_address=False)
        super_thing.setup(avahi_enable=False)
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        super_service = super_thing._get_function(super_service_name)
        super_schedule_msg = MXSuperScheduleMessage(ms_schedule_msg)

        # super_schedule_request의 scheduling을 시작하고 running이 True가 될 때까지 기다린다.
        super_service.start_super_schedule_thread(super_schedule_msg, super_thing._global_service_table, timeout=1)
        while not super_service._schedule_running:
            time.sleep(THREAD_TIME_OUT)
            
        time.sleep(0.001)

        # 정상적인 경우의 생성된 요청의 갯수를 가져온다.
        cnt = len(ms_result_schedule_check_msg_list)
        while cnt:
            # 생성된 check 요청 패킷 확인
            sm_schedule_msg = super_thing._publish_queue.get(timeout=0.5)
            if decode_MQTT_message(sm_schedule_msg)[1].get('status', '') == 'check':
                output_sm_schedule_check_msg_list.append(sm_schedule_msg)
                cnt -= 1
            else:
                assert False

        # 정상적인 check 스케줄 결과들을 넣어주고, 잘 처리하는지 확인
        time.sleep(schedule_check_delay)
        for msg in ms_result_schedule_check_msg_list:
            super_thing._handle_MS_RESULT_SCHEDULE(msg)

        if not super_service._schedule_running:
            output_sm_result_schedule_msg = get_schedule_result_msg(super_thing)
            return output_sm_schedule_check_msg_list, output_sm_schedule_confirm_msg_list, output_sm_result_schedule_msg

        # 정상적인 경우의 생성된 요청의 갯수를 가져온다.
        cnt = len(ms_result_schedule_confirm_msg_list)
        while cnt:
            # 생성된 confirm 요청 패킷 확인
            sm_schedule_msg = super_thing._publish_queue.get(timeout=0.5)
            if decode_MQTT_message(sm_schedule_msg)[1].get('status', '') == 'confirm':
                output_sm_schedule_confirm_msg_list.append(sm_schedule_msg)
                cnt -= 1
            else:
                assert False

        # 정상적인 confirm 스케줄 결과들을 넣어주고, 잘 처리하는지 확인
        time.sleep(schedule_confirm_delay)
        for msg in ms_result_schedule_confirm_msg_list:
            super_thing._handle_MS_RESULT_SCHEDULE(msg)

        if not super_service._schedule_running:
            output_sm_result_schedule_msg = get_schedule_result_msg(super_thing)
            return output_sm_schedule_check_msg_list, output_sm_schedule_confirm_msg_list, output_sm_result_schedule_msg

        # running이 False가 될 때까지 기다린다.
        while super_service._schedule_running:
            time.sleep(THREAD_TIME_OUT)
            
        time.sleep(0.001)

        # 최종 scheduling 결과가 오는 것을 모두 받아온다. (비정상적으로 2개의 결과를 보내는 경우를 감지하기 위함)
        while not super_thing._publish_queue.empty():
            output_sm_result_schedule_msg_list.append(super_thing._publish_queue.get())
        for msg in output_sm_result_schedule_msg_list:
            if 'SM/RESULT/SCHEDULE' in decode_MQTT_message(msg)[0]:
                output_sm_result_schedule_msg = msg

        return output_sm_schedule_check_msg_list, output_sm_schedule_confirm_msg_list, output_sm_result_schedule_msg

    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=expected_exception_message):
            task(ms_schedule_msg, ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list,
                 service_list_msg, register_result_msg, super_thing_name, super_service_name, schedule_check_delay, schedule_confirm_delay)
    else:
        output_sm_schedule_check_msg_list, output_sm_schedule_confirm_msg_list, output_sm_result_schedule_msg = \
            task(ms_schedule_msg, ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list,
                 service_list_msg, register_result_msg, super_thing_name, super_service_name, schedule_check_delay, schedule_confirm_delay)

        assert compare_mqtt_msg_list(output_sm_schedule_check_msg_list, expected_sm_schedule_check_msg_list)
        assert compare_mqtt_msg_list(output_sm_schedule_confirm_msg_list, expected_sm_schedule_confirm_msg_list)
        assert compare_mqtt_msg(output_sm_result_schedule_msg, expected_sm_result_schedule_msg)


####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING_OLD, [
    ('schedule_parallel_0', dict(service_list=service_list_result_input_level3_with_1_service,
                                 ms_schedule_topic_list=[
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0'],
                                 ms_schedule_payload_list=[
                                     {"scenario": "test1", "period": 10000},
                                     {"scenario": "test2", "period": 10000}],
                                 ms_result_schedule_check_msg_list=[encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test1", "status": "check"}),
                                                                    encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test2", "status": "check"})],
                                 ms_result_schedule_confirm_msg_list=[encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test1", "status": "confirm"}),
                                                                      encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test2", "status": "confirm"})]),
     dict(sm_result_schedule_topic_list=[
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0'],
        sm_result_schedule_payload_list=[
         {"error": 0, "scenario": "test1"},
         {"error": 0, "scenario": "test2"}]), None),
    ('schedule_parallel_1', dict(service_list=service_list_result_input_level3_with_1_service,
                                 ms_schedule_topic_list=[
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0'],
                                 ms_schedule_payload_list=[
                                     {"scenario": "test1", "period": 10000},
                                     {"scenario": "test2", "period": 10000},
                                     {"scenario": "test3", "period": 10000},
                                     {"scenario": "test4", "period": 10000},
                                     {"scenario": "test5", "period": 10000},
                                     {"scenario": "test6", "period": 10000},
                                     {"scenario": "test7", "period": 10000},
                                     {"scenario": "test8", "period": 10000},
                                     {"scenario": "test9", "period": 10000},
                                     {"scenario": "test10", "period": 10000}],
                                 ms_result_schedule_check_msg_list=[encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test1", "status": "check"}),
                                                                    encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test2", "status": "check"}),
                                                                    encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test3", "status": "check"}),
                                                                    encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test4", "status": "check"}),
                                                                    encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test5", "status": "check"}),
                                                                    encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test6", "status": "check"}),
                                                                    encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test7", "status": "check"}),
                                                                    encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test8", "status": "check"}),
                                                                    encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test9", "status": "check"}),
                                                                    encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test10", "status": "check"}),],
                                 ms_result_schedule_confirm_msg_list=[encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test1", "status": "confirm"}),
                                                                      encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test2", "status": "confirm"}),
                                                                      encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test3", "status": "confirm"}),
                                                                      encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test4", "status": "confirm"}),
                                                                      encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test5", "status": "confirm"}),
                                                                      encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test6", "status": "confirm"}),
                                                                      encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test7", "status": "confirm"}),
                                                                      encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test8", "status": "confirm"}),
                                                                      encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test9", "status": "confirm"}),
                                                                      encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test10", "status": "confirm"}),]),
     dict(sm_result_schedule_topic_list=[
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0'],
        sm_result_schedule_payload_list=[
         {"error": 0, "scenario": "test1"},
         {"error": 0, "scenario": "test2"},
         {"error": 0, "scenario": "test3"},
         {"error": 0, "scenario": "test4"},
         {"error": 0, "scenario": "test5"},
         {"error": 0, "scenario": "test6"},
         {"error": 0, "scenario": "test7"},
         {"error": 0, "scenario": "test8"},
         {"error": 0, "scenario": "test9"},
         {"error": 0, "scenario": "test10"}]), None),
    ('schedule_parallel_2', dict(service_list=service_list_result_input_level3_with_1_service,
                                 ms_schedule_topic_list=[
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                     'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0'],
                                 ms_schedule_payload_list=[
                                     {"scenario": "test1", "period": 10000},
                                     {"scenario": "test1", "period": 10000}],
                                 ms_result_schedule_check_msg_list=[encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                        payload={"error": 0, "scenario": "test1", "status": "check"})],
                                 ms_result_schedule_confirm_msg_list=[encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                                                          payload={"error": 0, "scenario": "test1", "status": "confirm"})]),
     dict(sm_result_schedule_topic_list=[
         'SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0'],
        sm_result_schedule_payload_list=[
         {"error": 0, "scenario": "test1"}]), None),
])
@pytest.mark.usefixtures('run_mosquitto')
def test_schedule_parallel(test_id: str, input: Dict[str, Union[str, List[str], List[dict]]], expected_output: Union[None, Exception], expected_exception_message: str):
    super_thing_name = 'super_thing_1'
    super_service_name = input['ms_schedule_topic_list'][0].split('/')[2]
    ms_schedule_msg_list = [encode_MQTT_message(topic=topic, payload=payload) for
                            topic, payload in zip(input['ms_schedule_topic_list'], input['ms_schedule_payload_list'])]
    ms_result_schedule_check_msg_list = input['ms_result_schedule_check_msg_list']
    ms_result_schedule_confirm_msg_list = input['ms_result_schedule_confirm_msg_list']

    expected_sm_result_schedule_list = [encode_MQTT_message(topic=topic, payload=payload) for
                                        topic, payload in zip(expected_output['sm_result_schedule_topic_list'], expected_output['sm_result_schedule_payload_list'])]

    service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing_name),
                                           payload=input['service_list'])
    register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing_name),
                                              payload={'error': 0, 'middleware_name': decode_MQTT_message(ms_schedule_msg_list[0])[0].split('/')[4]})

    def task(ms_schedule_msg_list, ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list, service_list_msg, register_result_msg, super_thing_name, super_service_name):
        output_sm_result_schedule_msg_list: List[mqtt.MQTTMessage] = []

        super_thing = MXBasicSuperThing(name=super_thing_name, append_mac_address=False)
        super_thing.setup(avahi_enable=False)
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)
        super_service = super_thing._get_function(super_service_name)

        for ms_schedule_msg in ms_schedule_msg_list:
            super_thing._handle_MS_SCHEDULE(MXSuperScheduleMessage(ms_schedule_msg))
            time.sleep(0.001)

        time.sleep(0.1)
        for msg in ms_result_schedule_check_msg_list:
            super_thing._handle_MS_RESULT_SCHEDULE(msg)

        time.sleep(0.1)
        for msg in ms_result_schedule_confirm_msg_list:
            super_thing._handle_MS_RESULT_SCHEDULE(msg)

        while not all([super_schedule_request._running == False for super_schedule_request in super_service._temporary_scheduling_table.values()]):
            time.sleep(THREAD_TIME_OUT)

        # 최종 scheduling 결과가 오는 것을 모두 받아온다. (비정상적으로 2개의 결과를 보내는 경우를 감지하기 위함)
        # 시나리오 이름이 중복되는 경우 ErrorCode를 담아서 리턴
        result_msg = []
        while not super_thing._publish_queue.empty():
            result_msg.append(super_thing._publish_queue.get())
        for msg in result_msg:
            if 'SM/RESULT/SCHEDULE' in decode_MQTT_message(msg)[0]:
                output_sm_result_schedule_msg_list.append(msg)

        return output_sm_result_schedule_msg_list

    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=expected_exception_message):
            task(ms_schedule_msg_list, ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list,
                 service_list_msg, register_result_msg, super_thing_name, super_service_name)
    else:
        output_sm_result_schedule_msg_list = task(ms_schedule_msg_list, ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list,
                                                  service_list_msg, register_result_msg, super_thing_name, super_service_name)

        assert compare_mqtt_msg_list(output_sm_result_schedule_msg_list, expected_sm_result_schedule_list, ignore_order=True)


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
