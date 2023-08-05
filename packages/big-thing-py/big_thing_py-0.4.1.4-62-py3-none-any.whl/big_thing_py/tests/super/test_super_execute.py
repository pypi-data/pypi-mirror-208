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
    ('super_execute_topic_0', dict(input_topic=f'MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                   service_list=service_list_result_input_level3_with_0_service),
     MXErrorCode.NO_ERROR, None),
    ('super_execute_topic_1', dict(input_topic=f'M3/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                   service_list=service_list_result_input_level3_with_1_service),
     False, None),
    ('super_execute_topic_2', dict(input_topic=f'MS/EX3CUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                   service_list=service_list_result_input_level3_with_1_service),
     False, None),
    ('super_execute_topic_3', dict(input_topic=f'MS/EXECUTE/not_exist_super_service/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                   service_list=service_list_result_input_level3_with_1_service),
     False, None),
    ('super_execute_topic_4', dict(input_topic=f'MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/not_exist_super_thing/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                   service_list=service_list_result_input_level3_with_1_service),
     False, None),
    ('super_execute_topic_5', dict(input_topic=f'MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/not_exist_super_middleware/SoPIoT-MW-Level1-0',
                                   service_list=service_list_result_input_level3_with_1_service),
     False, None),
])
def test_super_execute_topic_handle(test_id: str, input: Dict[str, str], expected_output: Union[bool, Exception], expected_exception_message: str):

    def setup(input: Dict[str, str]) -> Tuple[MXSuperThing, str]:
        super_thing = MXBasicSuperThing(name='super_thing_1', append_mac_address=False).setup(avahi_enable=False)
        execute_msg = encode_MQTT_message(topic=input['input_topic'], payload={"arguments": [{"order": 0, "value": 123.0}, {"order": 1, "value": 1.0}], "scenario": "test"})
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                               payload=service_list_result_input_level3_with_1_service)
        register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing.get_name()),
                                                  payload={'error': 0, 'middleware_name': 'SoPIoT-MW-Level3-0'})
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        schedule(super_thing)

        return super_thing, execute_msg

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

        time.sleep(0.01)

        while not super_thing._publish_queue.empty():
            super_thing._publish_queue.get()

    def task(super_thing: MXSuperThing, execute_msg: mqtt.MQTTMessage, expected_output):
        if isinstance(expected_output, MXErrorCode):
            super_thing._handle_mqtt_message(execute_msg)

            super_service_name = decode_MQTT_message(execute_msg)[0].split('/')[2]
            super_service = super_thing._get_function(super_service_name)
            super_thing._handle_MS_RESULT_EXECUTE(encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                                      payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"}))
            while super_service._running:
                time.sleep(0.01)

            time.sleep(0.01)

            while not super_service._publish_queue.empty():
                result_msg = super_service._publish_queue.get()
                if 'SM/RESULT/EXECUTE' in decode_MQTT_message(result_msg)[0]:
                    break
            error = MXErrorCode.get(decode_MQTT_message(result_msg)[1]['error'])
            return error
        else:
            rc = super_thing._handle_mqtt_message(execute_msg)
            return rc

    super_thing, execute_msg = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=expected_exception_message):
            task(super_thing, execute_msg, expected_output)
    else:
        output = task(super_thing, execute_msg, expected_output)
        assert output == expected_output


####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING_OLD, [
    ('super_execute_payload_0', dict(input_payload={
        "scenario": "test",
        "arguments": [
            {
                "order": 0,
                "value": 123
            },
            {
                "order": 1,
                "value": 1
            }
        ]
    }),
        MXErrorCode.NO_ERROR, None),
    ('super_execute_payload_1', dict(input_payload={
        "scenar": "test",
        "arguments": [
            {
                "order": 0,
                "value": 123
            },
            {
                "order": 1,
                "value": 1
            }
        ]
    }),
        False, r'.*'),
    ('super_execute_payload_2', dict(input_payload={
        "scenario": "",
        "arguments": [
            {
                "order": 0,
                "value": 123
            },
            {
                "order": 1,
                "value": 1
            }
        ]
    }),
        False, None),
    ('super_execute_payload_3', dict(input_payload={
        "scenario": "test",
        "argumen": [
            {
                "order": 0,
                "value": 123
            },
            {
                "order": 1,
                "value": 1
            }
        ]
    }),
        False, r'.*'),
    ('super_execute_payload_4', dict(input_payload={
        "scenario": "test",
        "arguments": [
            {
                "ord": 0,
                "value": 123
            },
            {
                "order": 1,
                "value": 1
            }
        ]
    }),
        False, None),
    ('super_execute_payload_5', dict(input_payload={
        "scenario": "test",
        "arguments": [
            {
                "order": "0",
                "value": 123
            },
            {
                "order": 1,
                "value": 1
            }
        ]
    }),
        False, None),
    ('super_execute_payload_6', dict(input_payload={
        "scenario": "test",
        "arguments": [
            {
                "order": 0,
                "val": 123
            },
            {
                "order": 1,
                "value": 1
            }
        ]
    }),
        False, None),
    ('super_execute_payload_7', dict(input_payload={
        "scenario": "test",
        "arguments": [
            {
                "order": 0,
                "value": 123.12
            },
            {
                "order": 1,
                "value": 1
            }
        ]
    }),
        MXErrorCode.NO_ERROR, None),
    ('super_execute_payload_8', dict(input_payload={
        "scenario": "test",
        "arguments": [
            {
                "order": 0,
                "value": "123"
            },
            {
                "order": 1,
                "value": 1
            }
        ]
    }),
        MXErrorCode.FAIL, None),
])
def test_super_execute_payload_handle(test_id: str, input: dict, expected_output: Union[None, Exception], expected_exception_message: str):

    def setup(input: Dict[str, str]) -> Tuple[MXSuperThing, str]:
        super_thing = MXBasicSuperThing(name='super_thing_1', append_mac_address=False).setup(avahi_enable=False)
        execute_msg = encode_MQTT_message(topic=f'MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                          payload=input['input_payload'])
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                               payload=service_list_result_input_level3_with_1_service)
        register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing.get_name()),
                                                  payload={'error': 0, 'middleware_name': 'SoPIoT-MW-Level3-0'})
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        return super_thing, execute_msg

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

        time.sleep(0.01)

        while not super_thing._publish_queue.empty():
            super_thing._publish_queue.get()

    def task(super_thing: MXSuperThing, execute_msg: mqtt.MQTTMessage, expected_output):
        schedule(super_thing)

        super_service_name = decode_MQTT_message(execute_msg)[0].split('/')[2]
        super_service = super_thing._get_function(super_service_name)

        if isinstance(expected_output, MXErrorCode):
            super_thing._handle_MS_EXECUTE(execute_msg)
            time.sleep(0.1)
            super_thing._handle_MS_RESULT_EXECUTE(encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                                      payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"}))
            while super_service._running:
                time.sleep(0.01)

            time.sleep(0.01)

            while not super_service._publish_queue.empty():
                result_msg = super_service._publish_queue.get()
                if 'SM/RESULT/EXECUTE' in decode_MQTT_message(result_msg)[0]:
                    break
            error = MXErrorCode.get(decode_MQTT_message(result_msg)[1]['error'])
            return error
        else:
            rc = super_thing._handle_MS_EXECUTE(execute_msg)
            return rc

    super_thing, execute_msg = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=expected_exception_message):
            output = task(super_thing, execute_msg, expected_output)
    else:
        output = task(super_thing, execute_msg, expected_output)
        assert output == expected_output


####################################################################################################################################

@pytest.mark.parametrize(PARAMETRIZE_STRING_OLD, [
    ('super_execute_0', dict(service_list=service_list_result_input_level3_with_1_service,
                             ms_schedule_msg=encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                                 payload={"scenario": "test", "period": 10000}),
                             ms_execute_msg=encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                                payload={"scenario": "test", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                             ms_result_schedule_check_msg_list=[
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                     payload={"error": 0, "scenario": "test", "status": "check"}),
                             ],
                             ms_result_schedule_confirm_msg_list=[
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                     payload={"error": 0, "scenario": "test", "status": "confirm"}),
                             ],
                             ms_result_execute_msg_list=[
                                 encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                     payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"}),
                             ]),
     dict(sm_schedule_check_msg_list=[
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
     ],
        sm_schedule_confirm_msg_list=[
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}),
     ],
        sm_execute_msg_list=[
            encode_MQTT_message(topic='SM/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                payload={"arguments": [{"order": 0, "value": 123.0}, {"order": 1, "value": 0.5}], "scenario": "test"}),
     ],
        sm_result_schedule_msg=encode_MQTT_message(topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                   payload={"error": 0, "scenario": "test"}),
        sm_result_execute_msg=encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                  payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"})), None),
    ('super_execute_1', dict(service_list=service_list_result_input_level3_with_3_service,
                             ms_schedule_msg=encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                                 payload={"scenario": "test", "period": 10000}),
                             ms_execute_msg=encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                                payload={"scenario": "test", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                             ms_result_schedule_check_msg_list=[
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                     payload={"error": 0, "scenario": "test", "status": "check"}),
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                     payload={"error": 0, "scenario": "test", "status": "check"}),
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                     payload={"error": 0, "scenario": "test", "status": "check"}),
                             ],
                             ms_result_schedule_confirm_msg_list=[
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                     payload={"error": 0, "scenario": "test", "status": "confirm"}),
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                     payload={"error": 0, "scenario": "test", "status": "confirm"}),
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                     payload={"error": 0, "scenario": "test", "status": "confirm"}),
                             ],
                             ms_result_execute_msg_list=[
                                 encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                     payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"}),
                                 encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                     payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"}),
                                 encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                     payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"}),
                             ]),
     dict(sm_schedule_check_msg_list=[
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
     ],
        sm_schedule_confirm_msg_list=[
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}),
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}),
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}),
     ],
        sm_execute_msg_list=[
            encode_MQTT_message(topic='SM/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                payload={"arguments": [{"order": 0, "value": 123.0}, {"order": 1, "value": 0.5}], "scenario": "test"}),
            encode_MQTT_message(topic='SM/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                payload={"arguments": [{"order": 0, "value": 123.0}, {"order": 1, "value": 0.5}], "scenario": "test"}),
            encode_MQTT_message(topic='SM/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                payload={"arguments": [{"order": 0, "value": 123.0}, {"order": 1, "value": 0.5}], "scenario": "test"}),
     ],
        sm_result_schedule_msg=encode_MQTT_message(topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                   payload={"error": 0, "scenario": "test"}),
        sm_result_execute_msg=encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                  payload={"error": 0, "return_type": "int", "return_value": 369.0, "scenario": "test"})), None),
    ('super_execute_2', dict(service_list=service_list_result_input_level3_with_1_service,
                             ms_schedule_msg=encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                                 payload={"scenario": "test", "period": 10000}),
                             ms_execute_msg=encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                                payload={"scenario": "test", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                             ms_result_schedule_check_msg_list=[
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                     payload={"error": 0, "scenario": "test", "status": "check"}),
                             ],
                             ms_result_schedule_confirm_msg_list=[
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                     payload={"error": 0, "scenario": "test", "status": "confirm"}),
                             ],
                             ms_result_execute_msg_list=[
                                 encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                     payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"}),
                             ]),
     dict(sm_schedule_check_msg_list=[
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                             payload={"period": 10000, "range": "single", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
     ],
        sm_schedule_confirm_msg_list=[
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                             payload={"period": 10000, "range": "single", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}),
     ],
        sm_execute_msg_list=[
            encode_MQTT_message(topic='SM/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                payload={"arguments": [{"order": 0, "value": 123.0}, {"order": 1, "value": 0.5}], "scenario": "test"}),
     ],
        sm_result_schedule_msg=encode_MQTT_message(topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                   payload={"error": 0, "scenario": "test"}),
        sm_result_execute_msg=encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                  payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"})), None),
    ('super_execute_3', dict(service_list=service_list_result_input_level3_with_3_service,
                             ms_schedule_msg=encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                                 payload={"scenario": "test", "period": 10000}),
                             ms_execute_msg=encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                                payload={"scenario": "test", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                             ms_result_schedule_check_msg_list=[
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                     payload={"error": 0, "scenario": "test", "status": "check"}),
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                     payload={"error": 0, "scenario": "test", "status": "check"}),
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                     payload={"error": 0, "scenario": "test", "status": "check"}),
                             ],
                             ms_result_schedule_confirm_msg_list=[
                                 encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                     payload={"error": 0, "scenario": "test", "status": "confirm"}),
                             ],
                             ms_result_execute_msg_list=[
                                 encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                                     payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"}),
                             ]),
     dict(sm_schedule_check_msg_list=[
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                             payload={"period": 10000, "range": "single", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                             payload={"period": 10000, "range": "single", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                             payload={"period": 10000, "range": "single", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
     ],
        sm_schedule_confirm_msg_list=[
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                             payload={"period": 10000, "range": "single", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}),
     ],
        sm_execute_msg_list=[
            encode_MQTT_message(topic='SM/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_SINGLE@0',
                                payload={"arguments": [{"order": 0, "value": 123.0}, {"order": 1, "value": 0.5}], "scenario": "test"}),
     ],
        sm_result_schedule_msg=encode_MQTT_message(topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                   payload={"error": 0, "scenario": "test"}),
        sm_result_execute_msg=encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_SINGLE/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                  payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"})), None),
])
def test_super_execute(test_id: str, input: Dict[str, Union[str, List[str], List[dict]]], expected_output: Union[None, Exception], expected_exception_message: str):

    def setup(input: Dict[str, str]) -> Tuple[MXSuperThing, str]:
        super_thing = MXBasicSuperThing(name='super_thing_1', append_mac_address=False).setup(avahi_enable=False)
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                               payload=input['service_list'])
        register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing.get_name()),
                                                  payload={'error': 0, 'middleware_name': 'SoPIoT-MW-Level3-0'})
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        ms_schedule_msg = input['ms_schedule_msg']
        ms_execute_msg = input['ms_execute_msg']

        ms_result_schedule_check_msg_list = input['ms_result_schedule_check_msg_list']
        ms_result_schedule_confirm_msg_list = input['ms_result_schedule_confirm_msg_list']
        ms_result_execute_msg_list = input['ms_result_execute_msg_list']

        schedule(super_thing, ms_schedule_msg, ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list)

        return super_thing, ms_execute_msg, ms_result_execute_msg_list

    def schedule(super_thing: MXSuperThing,
                 ms_schedule_msg: mqtt.MQTTMessage, ms_result_schedule_check_msg_list: mqtt.MQTTMessage, ms_result_schedule_confirm_msg_list: mqtt.MQTTMessage):
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

        time.sleep(0.01)

        while not super_thing._publish_queue.empty():
            super_thing._publish_queue.get()

    def task(super_thing: MXSuperThing, ms_execute_msg: mqtt.MQTTMessage, ms_result_execute_msg_list: mqtt.MQTTMessage):
        output_sm_execute_msg_list: List[mqtt.MQTTMessage] = []
        output_sm_result_execute_msg_list: List[mqtt.MQTTMessage] = []

        super_service_name = decode_MQTT_message(ms_execute_msg)[0].split('/')[2]
        super_service = super_thing._get_function(super_service_name)
        super_execute_msg = MXSuperExecuteMessage(ms_execute_msg)

        super_service.start_super_execute_thread(super_execute_msg=super_execute_msg, SUPER_SERVICE_REQUEST_KEY_TABLE=super_thing._SUPER_SERVICE_REQUEST_KEY_TABLE)
        while not super_service._running:
            time.sleep(0.01)

        time.sleep(0.01)

        cnt = len(ms_result_execute_msg_list)
        while cnt:
            sm_super_execute_msg = super_thing._publish_queue.get(timeout=0.5)
            output_sm_execute_msg_list.append(sm_super_execute_msg)
            cnt -= 1

        for msg in ms_result_execute_msg_list:
            super_thing._handle_MS_RESULT_EXECUTE(msg)

        # running이 False가 될 때까지 기다린다.
        while super_service._running:
            time.sleep(0.01)

        time.sleep(0.01)

        # 최종 scheduling 결과가 오는 것을 모두 받아온다. (비정상적으로 2개의 결과를 보내는 경우를 감지하기 위함)
        while not super_thing._publish_queue.empty():
            output_sm_result_execute_msg_list.append(super_thing._publish_queue.get())
        for msg in output_sm_result_execute_msg_list:
            if 'SM/RESULT/EXECUTE' in decode_MQTT_message(msg)[0]:
                output_sm_result_execute_msg = msg

        return output_sm_execute_msg_list, output_sm_result_execute_msg

    super_thing, ms_execute_msg, ms_result_execute_msg_list = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=expected_exception_message):
            output_sm_execute_msg_list, output_sm_result_execute_msg = task(super_thing, ms_execute_msg, ms_result_execute_msg_list)
    else:
        output_sm_execute_msg_list, output_sm_result_execute_msg = task(super_thing, ms_execute_msg, ms_result_execute_msg_list)

        assert compare_mqtt_msg_list(output_sm_execute_msg_list, expected_output['sm_execute_msg_list'])
        assert compare_mqtt_msg(output_sm_result_execute_msg, expected_output['sm_result_execute_msg'])

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING_OLD, [
    ('super_execute_arg_pass_0', dict(service_list=service_list_result_input_level3_with_3_service,
                                      ms_schedule_msg=encode_MQTT_message(topic=f'MS/SCHEDULE/super_multiple_sub_service_request_with_argument_pass/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                                          payload={"scenario": "test", "period": 10000}),
                                      ms_execute_msg=encode_MQTT_message(topic='MS/EXECUTE/super_multiple_sub_service_request_with_argument_pass/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                                         payload={"scenario": "test", "arguments": [{"order": 0, "value": 111}]}),
                                      ms_result_schedule_check_msg_list={
                                          'req1': [encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "scenario": "test", "status": "check"}),
                                                   encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "scenario": "test", "status": "check"}),
                                                   encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "scenario": "test", "status": "check"})],
                                          'req2': [encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "scenario": "test", "status": "check"}),
                                                   encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "scenario": "test", "status": "check"}),
                                                   encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "scenario": "test", "status": "check"})],
                                          'req3': [encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_no_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "scenario": "test", "status": "check"})]
                                      },
                                      ms_result_schedule_confirm_msg_list={
                                          'req1': [encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "scenario": "test", "status": "confirm"})],
                                          'req2': [encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "scenario": "test", "status": "confirm"}),
                                                   encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "scenario": "test", "status": "confirm"}),
                                                   encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "scenario": "test", "status": "confirm"})],
                                          'req3': [encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_no_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "scenario": "test", "status": "confirm"})]
                                      },
                                      ms_result_execute_msg_list={
                                          'req1': [encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "return_type": "int", "return_value": 111.0, "scenario": "test"})],
                                          'req2': [encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "return_type": "int", "return_value": 111.0, "scenario": "test"}),
                                                   encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "return_type": "int", "return_value": 111.0, "scenario": "test"}),
                                                   encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "return_type": "int", "return_value": 111.0, "scenario": "test"})],
                                          'req3': [encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_no_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                                                       payload={"error": 0, "return_type": "int", "return_value": 111.0, "scenario": "test"})]
                                      }),
     dict(sm_schedule_check_msg_list={
         'req1': [encode_MQTT_message(topic='SMl/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                      payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
                  encode_MQTT_message(topic='SMl/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                      payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
                  encode_MQTT_message(topic='SMl/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                      payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]})],
         'req2': [encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                      payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
                  encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                      payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
                  encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                      payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]})],
         'req3': [encode_MQTT_message(topic='SM/SCHEDULE/func_no_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                      payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]})]
     },
        sm_schedule_confirm_msg_list={
         'req1': [encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                      payload={"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]})],
         'req2': [encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                      payload={"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}),
                  encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                      payload={"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}),
                  encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                      payload={"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]})],
         'req3': [encode_MQTT_message(topic='SM/SCHEDULE/func_no_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                      payload={"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]})]
     },
        sm_execute_msg_list={
            'req1': [encode_MQTT_message(topic='SM/EXECUTE/func_with_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                         payload={"arguments": [{"order": 0, "value": 111.0}], "scenario": "test"})],
            'req2': [encode_MQTT_message(topic='SM/EXECUTE/func_with_arg/SUPER/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                         payload={"arguments": [{"order": 0, "value": 111.0}], "scenario": "test"}),
                     encode_MQTT_message(topic='SM/EXECUTE/func_with_arg/SUPER/SoPIoT-MW-Level2-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                         payload={"arguments": [{"order": 0, "value": 111.0}], "scenario": "test"}),
                     encode_MQTT_message(topic='SM/EXECUTE/func_with_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                         payload={"arguments": [{"order": 0, "value": 111.0}], "scenario": "test"})],
            'req3': [encode_MQTT_message(topic='SM/EXECUTE/func_no_arg/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_multiple_sub_service_request_with_argument_pass@0',
                                         payload={"arguments": [{"order": 0, "value": 111.0}], "scenario": "test"})]
     },
        sm_result_schedule_msg=encode_MQTT_message(topic='SM/RESULT/SCHEDULE/super_multiple_sub_service_request_with_argument_pass/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                   payload={"error": 0, "scenario": "test"}),
        sm_result_execute_msg=encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_multiple_sub_service_request_with_argument_pass/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                  payload={"error": 0, "return_type": "int", "return_value": 555.0, "scenario": "test"})), None),
])
@pytest.mark.skip(reason='not implemented yet')
def test_super_execute_arg_pass(test_id: str, input: Dict[str, Union[str, List[str], List[dict]]], expected_output: Union[None, Exception], expected_exception_message: str):

    def setup(input: Dict[str, str]) -> Tuple[MXSuperThing, str]:
        super_thing = MXBasicSuperThing(name='super_thing_1', append_mac_address=False).setup(avahi_enable=False)
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                               payload=input['service_list'])
        register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing.get_name()),
                                                  payload={'error': 0, 'middleware_name': 'SoPIoT-MW-Level3-0'})
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        ms_schedule_msg = input['ms_schedule_msg']
        ms_execute_msg = input['ms_execute_msg']

        ms_result_schedule_check_msg_list = input['ms_result_schedule_check_msg_list']
        ms_result_schedule_confirm_msg_list = input['ms_result_schedule_confirm_msg_list']
        ms_result_execute_msg_list = input['ms_result_execute_msg_list']

        schedule(super_thing, ms_schedule_msg, ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list)

        return super_thing, ms_execute_msg, ms_result_execute_msg_list

    def schedule(super_thing: MXSuperThing,
                 ms_schedule_msg: mqtt.MQTTMessage, ms_result_schedule_check_msg_list: dict, ms_result_schedule_confirm_msg_list: dict):
        super_thing._handle_mqtt_message(ms_schedule_msg)

        for check_msg_list, confirm_msg_list in zip(ms_result_schedule_check_msg_list.values(), ms_result_schedule_confirm_msg_list.values()):
            cnt = len(check_msg_list)
            while cnt:
                sm_schedule_msg = super_thing._publish_queue.get(timeout=0.5)
                if decode_MQTT_message(sm_schedule_msg)[1].get('status', '') == 'check':
                    cnt -= 1
                else:
                    assert False

            for msg in check_msg_list:
                super_thing._handle_MS_RESULT_SCHEDULE(msg)

            cnt = len(confirm_msg_list)
            while cnt:
                sm_schedule_msg = super_thing._publish_queue.get(timeout=0.5)
                if decode_MQTT_message(sm_schedule_msg)[1].get('status', '') == 'confirm':
                    cnt -= 1
                else:
                    assert False

            for msg in confirm_msg_list:
                super_thing._handle_MS_RESULT_SCHEDULE(msg)

        time.sleep(0.1)

        # while not super_thing._publish_queue.empty():
        #     super_thing._publish_queue.get()

    def task(super_thing: MXSuperThing, ms_execute_msg: mqtt.MQTTMessage, ms_result_execute_msg_list: mqtt.MQTTMessage):
        output_sm_execute_msg_list: List[mqtt.MQTTMessage] = []
        output_sm_result_execute_msg_list: List[mqtt.MQTTMessage] = []

        super_service_name = decode_MQTT_message(ms_execute_msg)[0].split('/')[2]
        super_service = super_thing._get_function(super_service_name)
        super_execute_msg = MXSuperExecuteMessage(ms_execute_msg)

        super_service.start_super_execute_thread(super_execute_msg=super_execute_msg, SUPER_SERVICE_REQUEST_KEY_TABLE=super_thing._SUPER_SERVICE_REQUEST_KEY_TABLE)
        while not super_service._running:
            time.sleep(0.01)

        time.sleep(0.01)

        cnt = len(ms_result_execute_msg_list)
        while cnt:
            sm_super_execute_msg = super_thing._publish_queue.get(timeout=0.5)
            output_sm_execute_msg_list.append(sm_super_execute_msg)
            cnt -= 1

        for msg in ms_result_execute_msg_list:
            super_thing._handle_MS_RESULT_EXECUTE(msg)

        # running이 False가 될 때까지 기다린다.
        while super_service._running:
            time.sleep(0.01)

        time.sleep(0.01)

        # 최종 scheduling 결과가 오는 것을 모두 받아온다. (비정상적으로 2개의 결과를 보내는 경우를 감지하기 위함)
        while not super_thing._publish_queue.empty():
            output_sm_result_execute_msg_list.append(super_thing._publish_queue.get())
        for msg in output_sm_result_execute_msg_list:
            if 'SM/RESULT/EXECUTE' in decode_MQTT_message(msg)[0]:
                output_sm_result_execute_msg = msg

        return output_sm_execute_msg_list, output_sm_result_execute_msg

    super_thing, ms_execute_msg, ms_result_execute_msg_list = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=expected_exception_message):
            output_sm_execute_msg_list, output_sm_result_execute_msg = task(super_thing, ms_execute_msg, ms_result_execute_msg_list)
    else:
        output_sm_execute_msg_list, output_sm_result_execute_msg = task(super_thing, ms_execute_msg, ms_result_execute_msg_list)

        assert compare_mqtt_msg_list(output_sm_execute_msg_list, expected_output['sm_execute_msg_list'])
        assert compare_mqtt_msg(output_sm_result_execute_msg, expected_output['sm_result_execute_msg'])

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING_OLD, [
    ('super_execute_timeout_0', dict(service_list=service_list_result_input_level3_with_1_service,
                         ms_schedule_msg=encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                             payload={"scenario": "test", "period": 10000}),
                         ms_execute_msg=encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                            payload={"scenario": "test", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                         ms_result_schedule_check_msg_list=[
                             encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                 payload={"error": 0, "scenario": "test", "status": "check"}),
                         ],
        ms_result_schedule_confirm_msg_list=[
                             encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                 payload={"error": 0, "scenario": "test", "status": "confirm"}),
                         ],
        ms_result_execute_msg_list=[
                             encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                 payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"}),
                         ],
        execute_delay=0.5),
     dict(sm_schedule_check_msg_list=[
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
     ],
        sm_schedule_confirm_msg_list=[
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}),
     ],
        sm_execute_msg_list=[
         encode_MQTT_message(topic='SM/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"arguments": [{"order": 0, "value": 123.0}, {"order": 1, "value": 0.5}], "scenario": "test"}),
     ],
        sm_result_schedule_msg=encode_MQTT_message(topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                   payload={"error": 0, "scenario": "test"}),
        sm_result_execute_msg=encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                  payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"})), None),
    ('super_execute_timeout_1', dict(service_list=service_list_result_input_level3_with_1_service,
                                     ms_schedule_msg=encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                                         payload={"scenario": "test", "period": 10000}),
                                     ms_execute_msg=encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                                        payload={"scenario": "test", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 1.5}]}),
                                     ms_result_schedule_check_msg_list=[
                                         encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                             payload={"error": 0, "scenario": "test", "status": "check"}),
                                     ],
                                     ms_result_schedule_confirm_msg_list=[
                                         encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                             payload={"error": 0, "scenario": "test", "status": "confirm"}),
                                     ],
                                     ms_result_execute_msg_list=[
                                         encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test"}),
                                     ],
                                     execute_delay=1.5),
     dict(sm_schedule_check_msg_list=[
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"period": 10000, "range": "all", "scenario": "test", "status": "check", "tag_list": [{"name": "basic"}]}),
     ],
        sm_schedule_confirm_msg_list=[
         encode_MQTT_message(topic='SM/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"period": 10000, "range": "all", "scenario": "test", "status": "confirm", "tag_list": [{"name": "basic"}]}),
     ],
        sm_execute_msg_list=[
         encode_MQTT_message(topic='SM/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                             payload={"arguments": [{"order": 0, "value": 123.0}, {"order": 1, "value": 1.5}], "scenario": "test"}),
     ],
        sm_result_schedule_msg=encode_MQTT_message(topic='SM/RESULT/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                   payload={"error": 0, "scenario": "test"}),
        sm_result_execute_msg=encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                  payload={"error": -2, "return_type": "int", "return_value": None, "scenario": "test"})), None),
])
def test_super_execute_timeout(test_id: str, input: Dict[str, Union[str, List[str], List[dict]]], expected_output: Union[None, Exception], expected_exception_message: str):

    def setup(input: Dict[str, str]) -> Tuple[MXSuperThing, str]:
        super_thing = MXBasicSuperThing(name='super_thing_1', append_mac_address=False).setup(avahi_enable=False)
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                               payload=input['service_list'])
        register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing.get_name()),
                                                  payload={'error': 0, 'middleware_name': 'SoPIoT-MW-Level3-0'})
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        ms_schedule_msg = input['ms_schedule_msg']
        ms_execute_msg = input['ms_execute_msg']

        ms_result_schedule_check_msg_list = input['ms_result_schedule_check_msg_list']
        ms_result_schedule_confirm_msg_list = input['ms_result_schedule_confirm_msg_list']
        ms_result_execute_msg_list = input['ms_result_execute_msg_list']
        execute_delay = input['execute_delay']

        schedule(super_thing, ms_schedule_msg, ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list)

        return super_thing, ms_execute_msg, ms_result_execute_msg_list, execute_delay

    def schedule(super_thing: MXSuperThing,
                 ms_schedule_msg: mqtt.MQTTMessage, ms_result_schedule_check_msg_list: mqtt.MQTTMessage, ms_result_schedule_confirm_msg_list: mqtt.MQTTMessage):
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

        time.sleep(0.01)

        while not super_thing._publish_queue.empty():
            super_thing._publish_queue.get()

    def task(super_thing: MXSuperThing, ms_execute_msg: mqtt.MQTTMessage, ms_result_execute_msg_list: mqtt.MQTTMessage, execute_delay: float):
        output_sm_execute_msg_list: List[mqtt.MQTTMessage] = []
        output_sm_result_execute_msg_list: List[mqtt.MQTTMessage] = []

        super_service_name = decode_MQTT_message(ms_execute_msg)[0].split('/')[2]
        super_service = super_thing._get_function(super_service_name)
        super_execute_msg = MXSuperExecuteMessage(ms_execute_msg)

        super_service.start_super_execute_thread(super_execute_msg=super_execute_msg, SUPER_SERVICE_REQUEST_KEY_TABLE=super_thing._SUPER_SERVICE_REQUEST_KEY_TABLE)
        while not super_service._running:
            time.sleep(0.01)

        time.sleep(0.01)

        cnt = len(ms_result_execute_msg_list)
        while cnt:
            sm_super_execute_msg = super_thing._publish_queue.get(timeout=0.5)
            output_sm_execute_msg_list.append(sm_super_execute_msg)
            cnt -= 1

        time.sleep(execute_delay)
        for msg in ms_result_execute_msg_list:
            super_thing._handle_MS_RESULT_EXECUTE(msg)

        # running이 False가 될 때까지 기다린다.
        while super_service._running:
            time.sleep(0.01)

        time.sleep(0.01)

        # 최종 scheduling 결과가 오는 것을 모두 받아온다. (비정상적으로 2개의 결과를 보내는 경우를 감지하기 위함)
        while not super_thing._publish_queue.empty():
            output_sm_result_execute_msg_list.append(super_thing._publish_queue.get())
        for msg in output_sm_result_execute_msg_list:
            if 'SM/RESULT/EXECUTE' in decode_MQTT_message(msg)[0]:
                output_sm_result_execute_msg = msg

        return output_sm_execute_msg_list, output_sm_result_execute_msg

    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=expected_exception_message):
            super_thing, ms_execute_msg, ms_result_execute_msg_list, execute_delay = setup(input)
            output_sm_execute_msg_list, output_sm_result_execute_msg = task(super_thing, ms_execute_msg, ms_result_execute_msg_list, execute_delay)
    else:
        super_thing, ms_execute_msg, ms_result_execute_msg_list, execute_delay = setup(input)
        output_sm_execute_msg_list, output_sm_result_execute_msg = task(super_thing, ms_execute_msg, ms_result_execute_msg_list, execute_delay)

        assert compare_mqtt_msg_list(output_sm_execute_msg_list, expected_output['sm_execute_msg_list'])
        assert compare_mqtt_msg(output_sm_result_execute_msg, expected_output['sm_result_execute_msg'])

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING_OLD, [
    ('super_execute_parallel_0', dict(service_list=service_list_result_input_level3_with_1_service,
                         ms_schedule_msg_list=[
                             encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                 payload={"scenario": "test1", "period": 10000}),
                             encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                 payload={"scenario": "test2", "period": 10000}),
                         ],
        ms_execute_msg_list=[
                             encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                 payload={"scenario": "test1", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                             encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                 payload={"scenario": "test2", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                         ],
        ms_result_schedule_check_msg_list=[
                             encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                 payload={"error": 0, "scenario": "test1", "status": "check"}),
                             encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                 payload={"error": 0, "scenario": "test2", "status": "check"}),
                         ],
        ms_result_schedule_confirm_msg_list=[
                             encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                 payload={"error": 0, "scenario": "test1", "status": "confirm"}),
                             encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                 payload={"error": 0, "scenario": "test2", "status": "confirm"}),
                         ],
        ms_result_execute_msg_list=[
                             encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                 payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test1"}),
                             encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                 payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test2"}),
                         ]),
     dict(sm_result_execute_msg_list=[
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test1"}),
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test2"}),
     ]), None),
    ('super_execute_parallel_1', dict(service_list=service_list_result_input_level3_with_1_service,
                                      ms_schedule_msg_list=[
                                          encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test1", "period": 10000}),
                                          encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test2", "period": 10000}),
                                          encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test3", "period": 10000}),
                                          encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test4", "period": 10000}),
                                          encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test5", "period": 10000}),
                                          encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test6", "period": 10000}),
                                          encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test7", "period": 10000}),
                                          encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test8", "period": 10000}),
                                          encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test9", "period": 10000}),
                                          encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test10", "period": 10000}),
                                      ],
                                      ms_execute_msg_list=[
                                          encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test1", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                                          encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test2", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                                          encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test3", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                                          encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test4", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                                          encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test5", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                                          encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test6", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                                          encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test7", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                                          encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test8", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                                          encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test9", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                                          encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test10", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                                      ],
                                      ms_result_schedule_check_msg_list=[
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test1", "status": "check"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test2", "status": "check"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test3", "status": "check"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test4", "status": "check"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test5", "status": "check"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test6", "status": "check"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test7", "status": "check"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test8", "status": "check"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test9", "status": "check"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test10", "status": "check"}),
                                      ],
                                      ms_result_schedule_confirm_msg_list=[
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test1", "status": "confirm"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test2", "status": "confirm"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test3", "status": "confirm"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test4", "status": "confirm"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test5", "status": "confirm"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test6", "status": "confirm"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test7", "status": "confirm"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test8", "status": "confirm"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test9", "status": "confirm"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test10", "status": "confirm"}),
                                      ],
                                      ms_result_execute_msg_list=[
                                          encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test1"}),
                                          encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test2"}),
                                          encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test3"}),
                                          encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test4"}),
                                          encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test5"}),
                                          encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test6"}),
                                          encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test7"}),
                                          encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test8"}),
                                          encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test9"}),
                                          encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test10"}),
                                      ]),
     dict(sm_result_execute_msg_list=[
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test1"}),
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test2"}),
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test3"}),
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test4"}),
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test5"}),
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test6"}),
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test7"}),
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test8"}),
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test9"}),
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test10"}),
     ]), None),
    ('super_execute_parallel_2', dict(service_list=service_list_result_input_level3_with_1_service,
                                      ms_schedule_msg_list=[
                                          encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test1", "period": 10000}),
                                          encode_MQTT_message(topic=f'MS/SCHEDULE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test2", "period": 10000}),
                                      ],
                                      ms_execute_msg_list=[
                                          encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test1", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                                          encode_MQTT_message(topic='MS/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                                                              payload={"scenario": "test1", "arguments": [{"order": 0, "value": 123}, {"order": 1, "value": 0.5}]}),
                                      ],
                                      ms_result_schedule_check_msg_list=[
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test1", "status": "check"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test2", "status": "check"}),
                                      ],
                                      ms_result_schedule_confirm_msg_list=[
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test1", "status": "confirm"}),
                                          encode_MQTT_message(topic='MS/RESULT/SCHEDULE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "scenario": "test2", "status": "confirm"}),
                                      ],
                                      ms_result_execute_msg_list=[
                                          encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test1"}),
                                          encode_MQTT_message(topic='MS/RESULT/EXECUTE/func_with_arg_and_delay/SUPER/SoPIoT-MW-Level1-0/SoPIoT-MW-Level1-0@super_thing_1@super_func_execute_func_with_arg_and_delay_ALL@0',
                                                              payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test1"}),
                                      ]),
     dict(sm_result_execute_msg_list=[
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": 0, "return_type": "int", "return_value": 123.0, "scenario": "test1"}),
         encode_MQTT_message(topic='SM/RESULT/EXECUTE/super_func_execute_func_with_arg_and_delay_ALL/super_thing_1/SoPIoT-MW-Level3-0/SoPIoT-MW-Level1-0',
                             payload={"error": -4, "return_type": "int", "return_value": None, "scenario": "test1"}),
     ]), None),
])
# @pytest.mark.skip(reason="This test is not implemented yet.")
def test_super_execute_parallel(test_id: str, input: Dict[str, Union[str, List[str], List[dict]]], expected_output: Union[None, Exception], expected_exception_message: str):

    def setup(input: Dict[str, str]) -> Tuple[MXSuperThing, str]:
        super_thing = MXBasicSuperThing(name='super_thing_1', append_mac_address=False).setup(avahi_enable=False)
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                               payload=input['service_list'])
        register_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (super_thing.get_name()),
                                                  payload={'error': 0, 'middleware_name': 'SoPIoT-MW-Level3-0'})
        super_thing._handle_MT_RESULT_REGISTER(register_result_msg)
        super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)

        ms_schedule_msg_list = input['ms_schedule_msg_list']
        ms_execute_msg_list = input['ms_execute_msg_list']

        ms_result_schedule_check_msg_list = input['ms_result_schedule_check_msg_list']
        ms_result_schedule_confirm_msg_list = input['ms_result_schedule_confirm_msg_list']
        ms_result_execute_msg_list = input['ms_result_execute_msg_list']

        schedule(super_thing, ms_schedule_msg_list, ms_result_schedule_check_msg_list, ms_result_schedule_confirm_msg_list)

        return super_thing, ms_execute_msg_list, ms_result_execute_msg_list

    def schedule(super_thing: MXSuperThing,
                 ms_schedule_msg_list: mqtt.MQTTMessage, ms_result_schedule_check_msg_list: mqtt.MQTTMessage, ms_result_schedule_confirm_msg_list: mqtt.MQTTMessage):
        for ms_schedule_msg in ms_schedule_msg_list:
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

        time.sleep(0.01)

        while not super_thing._publish_queue.empty():
            super_thing._publish_queue.get()

    def task(super_thing: MXSuperThing, ms_execute_msg_list: mqtt.MQTTMessage, ms_result_execute_msg_list: mqtt.MQTTMessage):
        output_sm_result_execute_msg_list: List[mqtt.MQTTMessage] = []

        for ms_execute_msg in ms_execute_msg_list:
            super_service_name = decode_MQTT_message(ms_execute_msg)[0].split('/')[2]
            super_service = super_thing._get_function(super_service_name)
            super_execute_msg = MXSuperExecuteMessage(ms_execute_msg)
            super_thing._handle_MS_EXECUTE(super_execute_msg)
            time.sleep(0.01)

        time.sleep(0.1)
        for msg in ms_result_execute_msg_list:
            super_thing._handle_MS_RESULT_EXECUTE(msg)

        while not all([super_service_execute_request._running == False for super_service_execute_request in super_service._mapping_table.values()]):
            time.sleep(0.01)

        # 최종 scheduling 결과가 오는 것을 모두 받아온다. (비정상적으로 2개의 결과를 보내는 경우를 감지하기 위함)
        # 시나리오 이름이 중복되는 경우 ErrorCode를 담아서 리턴
        result_msg = []
        while not super_thing._publish_queue.empty():
            result_msg.append(super_thing._publish_queue.get())
        for msg in result_msg:
            if 'SM/RESULT/EXECUTE' in decode_MQTT_message(msg)[0]:
                output_sm_result_execute_msg_list.append(msg)

        return output_sm_result_execute_msg_list

    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=expected_exception_message):
            super_thing, ms_execute_msg_list, ms_result_execute_msg_list = setup(input)
            output_sm_result_execute_msg_list = task(super_thing, ms_execute_msg_list, ms_result_execute_msg_list)
    else:
        super_thing, ms_execute_msg_list, ms_result_execute_msg_list = setup(input)
        output_sm_result_execute_msg_list = task(super_thing, ms_execute_msg_list, ms_result_execute_msg_list)

        assert compare_mqtt_msg_list(output_sm_result_execute_msg_list, expected_output['sm_result_execute_msg_list'], ignore_order=True)


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
