from big_thing_py.tests.thing_factory import *
from big_thing_py.tests.conftest import PARAMETRIZE_STRING, compare_mqtt_msg, compare_mqtt_msg_list
import pytest


reg_gen_0_thing = BigThingFactory().create_type_A_thing()
reg_gen_1_thing = BigThingFactory().create_type_B_thing()
reg_gen_2_thing = BigThingFactory().create_type_C_thing()
reg_gen_3_thing = BigThingFactory().create_type_D_thing()
reg_gen_4_thing = BigThingFactory().create_type_E_thing()
reg_gen_5_thing = BigThingFactory().create_type_F_thing()
reg_gen_6_thing = BigThingFactory().create_type_G_thing()
reg_gen_7_thing = BigThingFactory().create_type_H_thing()
reg_gen_8_thing = BigThingFactory().create_type_I_thing()
reg_gen_9_thing = BigThingFactory().create_type_J_thing()


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('reg_gen_0', reg_gen_0_thing,
     encode_MQTT_message(topic=MXProtocolType.Base.TM_REGISTER.value % (reg_gen_0_thing.get_name()), payload={'name': 'test_thing', 'alive_cycle': 60, 'is_super': False, 'is_parallel': True, 'values': [{'name': 'value1', 'description': '', 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}, 'format': ''}, {'name': 'value2', 'description': '', 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}, 'format': ''}], 'functions': [{'name': '__value1', 'description': '', 'exec_time': 0, 'return_type': 'int', 'energy': 0, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 0, 'arguments': []}, {'name': '__value2', 'description': '', 'exec_time': 0, 'return_type': 'int', 'energy': 0, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 0, 'arguments': []}, {'name': 'function1', 'description': '', 'exec_time': 1000, 'return_type': 'int', 'energy': 100, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 1, 'arguments': [{'name': 'arg1', 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg2', 'type': 'double', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg3', 'type': 'string', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg4', 'type': 'bool', 'bound': {'min_value': 0, 'max_value': 100}}]}, {'name': 'function2', 'description': '', 'exec_time': 1000, 'return_type': 'int', 'energy': 100, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 1, 'arguments': [{'name': 'arg1', 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg2', 'type': 'double', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg3', 'type': 'string', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg4', 'type': 'bool', 'bound': {'min_value': 0, 'max_value': 100}}]}]})),
    ('reg_gen_1', reg_gen_1_thing,
     encode_MQTT_message(topic=MXProtocolType.Base.TM_REGISTER.value % (reg_gen_1_thing.get_name()), payload={'name': 'default_big_thing', 'alive_cycle': 60, 'is_super': False, 'is_parallel': True, 'values': [{'name': 'value1', 'description': '', 'tags': [{'name': 'default_big_thing'}, {'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}], 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}, 'format': ''}, {'name': 'value2', 'description': '', 'tags': [{'name': 'default_big_thing'}, {'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}], 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}, 'format': ''}], 'functions': [{'name': '__value1', 'description': '', 'exec_time': 0, 'return_type': 'int', 'energy': 0, 'tags': [{'name': 'default_big_thing'}, {'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}], 'use_arg': 0, 'arguments': []}, {'name': '__value2', 'description': '', 'exec_time': 0, 'return_type': 'int', 'energy': 0, 'tags': [{'name': 'default_big_thing'}, {'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}], 'use_arg': 0, 'arguments': []}, {'name': 'function1', 'description': '', 'exec_time': 1000, 'return_type': 'int', 'energy': 100, 'tags': [{'name': 'default_big_thing'}, {'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}], 'use_arg': 1, 'arguments': [{'name': 'arg1', 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg2', 'type': 'double', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg3', 'type': 'string', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg4', 'type': 'bool', 'bound': {'min_value': 0, 'max_value': 100}}]}, {'name': 'function2', 'description': '', 'exec_time': 1000, 'return_type': 'int', 'energy': 100, 'tags': [{'name': 'default_big_thing'}, {'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}], 'use_arg': 1, 'arguments': [{'name': 'arg1', 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg2', 'type': 'double', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg3', 'type': 'string', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg4', 'type': 'bool', 'bound': {'min_value': 0, 'max_value': 100}}]}]})),
    ('reg_gen_2', reg_gen_2_thing,
     encode_MQTT_message(topic=MXProtocolType.Base.TM_REGISTER.value % (reg_gen_2_thing.get_name()), payload={'name': 'test_thing', 'alive_cycle': 60, 'is_super': False, 'is_parallel': True, 'values': [], 'functions': []})),
    ('reg_gen_3', reg_gen_3_thing,
     False),
    ('reg_gen_4', reg_gen_4_thing,
     encode_MQTT_message(topic=MXProtocolType.Base.TM_REGISTER.value % (reg_gen_4_thing.get_name()), payload={'name': 'test_thing', 'alive_cycle': 60, 'is_super': False, 'is_parallel': True, 'values': [{'name': 'value1', 'description': '', 'tags': [{'name': 'test_thing'}], 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}, 'format': ''}, {'name': 'value2', 'description': '', 'tags': [{'name': 'test_thing'}], 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}, 'format': ''}], 'functions': [{'name': '__value1', 'description': '', 'exec_time': 0, 'return_type': 'int', 'energy': 0, 'tags': [{'name': 'test_thing'}], 'use_arg': 0, 'arguments': []}, {'name': '__value2', 'description': '', 'exec_time': 0, 'return_type': 'int', 'energy': 0, 'tags': [{'name': 'test_thing'}], 'use_arg': 0, 'arguments': []}, {'name': 'function1', 'description': '', 'exec_time': 1000, 'return_type': 'int', 'energy': 100, 'tags': [{'name': 'test_thing'}], 'use_arg': 1, 'arguments': [{'name': 'arg1', 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg2', 'type': 'double', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg3', 'type': 'string', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg4', 'type': 'bool', 'bound': {'min_value': 0, 'max_value': 100}}]}, {'name': 'function2', 'description': '', 'exec_time': 1000, 'return_type': 'int', 'energy': 100, 'tags': [{'name': 'test_thing'}], 'use_arg': 1, 'arguments': [{'name': 'arg1', 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg2', 'type': 'double', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg3', 'type': 'string', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg4', 'type': 'bool', 'bound': {'min_value': 0, 'max_value': 100}}]}]})),
    ('reg_gen_5', reg_gen_5_thing,
     encode_MQTT_message(topic=MXProtocolType.Base.TM_REGISTER.value % (reg_gen_5_thing.get_name()), payload={'name': 'test_thing', 'alive_cycle': 60, 'is_super': False, 'is_parallel': True, 'values': [{'name': '', 'description': '', 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}, 'format': ''}, {'name': '', 'description': '', 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}, 'format': ''}], 'functions': [{'name': '', 'description': '', 'exec_time': 1000, 'return_type': 'int', 'energy': 100, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 1, 'arguments': [{'name': 'arg1', 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg2', 'type': 'double', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg3', 'type': 'string', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg4', 'type': 'bool', 'bound': {'min_value': 0, 'max_value': 100}}]}, {'name': '', 'description': '', 'exec_time': 1000, 'return_type': 'int', 'energy': 100, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 1, 'arguments': [{'name': 'arg1', 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg2', 'type': 'double', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg3', 'type': 'string', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg4', 'type': 'bool', 'bound': {'min_value': 0, 'max_value': 100}}]}, {'name': '__', 'description': '', 'exec_time': 0, 'return_type': 'int', 'energy': 0, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 0, 'arguments': []}, {'name': '__', 'description': '', 'exec_time': 0, 'return_type': 'int', 'energy': 0, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 0, 'arguments': []}]})),
    ('reg_gen_6', reg_gen_6_thing,
     encode_MQTT_message(topic=MXProtocolType.Base.TM_REGISTER.value % (reg_gen_6_thing.get_name()), payload={'name': 'test_thing', 'alive_cycle': 60, 'is_super': False, 'is_parallel': True, 'values': [{'name': 'value1', 'description': '', 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}, 'format': 'something'}, {'name': 'value2', 'description': '', 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}, 'format': 'something'}], 'functions': [{'name': '__value1', 'description': '', 'exec_time': 0, 'return_type': 'int', 'energy': 0, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 0, 'arguments': []}, {'name': '__value2', 'description': '', 'exec_time': 0, 'return_type': 'int', 'energy': 0, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 0, 'arguments': []}, {'name': 'function1', 'description': '', 'exec_time': 1000, 'return_type': 'int', 'energy': 100, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 1, 'arguments': [{'name': 'arg1', 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg2', 'type': 'double', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg3', 'type': 'string', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg4', 'type': 'bool', 'bound': {'min_value': 0, 'max_value': 100}}]}, {'name': 'function2', 'description': '', 'exec_time': 1000, 'return_type': 'int', 'energy': 100, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 1, 'arguments': [{'name': 'arg1', 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg2', 'type': 'double', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg3', 'type': 'string', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg4', 'type': 'bool', 'bound': {'min_value': 0, 'max_value': 100}}]}]})),
    ('reg_gen_7', reg_gen_7_thing,
     encode_MQTT_message(topic=MXProtocolType.Base.TM_REGISTER.value % (reg_gen_7_thing.get_name()), payload={'name': 'test_thing', 'alive_cycle': 60, 'is_super': False, 'is_parallel': True, 'values': [{'name': 'value1', 'description': '', 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}, 'format': ''}, {'name': 'value2', 'description': '', 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}, 'format': ''}], 'functions': [{'name': '__value1', 'description': '', 'exec_time': 0, 'return_type': 'int', 'energy': 0, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 0, 'arguments': []}, {'name': '__value2', 'description': '', 'exec_time': 0, 'return_type': 'int', 'energy': 0, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 0, 'arguments': []}, {'name': 'function1', 'description': '', 'exec_time': -10000, 'return_type': 'int', 'energy': -10, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 1, 'arguments': [{'name': 'arg1', 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg2', 'type': 'double', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg3', 'type': 'string', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg4', 'type': 'bool', 'bound': {'min_value': 0, 'max_value': 100}}]}, {'name': 'function2', 'description': '', 'exec_time': -10000, 'return_type': 'int', 'energy': -10, 'tags': [{'name': 'tag1'}, {'name': 'tag2'}, {'name': 'tag3'}, {'name': 'test_thing'}], 'use_arg': 1, 'arguments': [{'name': 'arg1', 'type': 'int', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg2', 'type': 'double', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg3', 'type': 'string', 'bound': {'min_value': 0, 'max_value': 100}}, {'name': 'arg4', 'type': 'bool', 'bound': {'min_value': 0, 'max_value': 100}}]}]})),
    ('reg_gen_8', reg_gen_8_thing,
     False),
    ('reg_gen_9', reg_gen_9_thing,
     False)
])
def test_generate_register_message(test_id: str, input: MXBigThing, expected_output: Union[dict, bool]):

    def setup(input) -> MXBigThing:
        big_thing = input
        return big_thing

    def task(big_thing: MXBigThing) -> MXTag:
        reg_msg = big_thing._generate_register_message()
        if isinstance(reg_msg, MXMQTTMessage):
            topic = reg_msg.topic
            payload = reg_msg.payload
            msg = encode_MQTT_message(topic, payload)
        else:
            msg = reg_msg
        return msg

    big_thing = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing)
    else:
        output = task(big_thing)
        if isinstance(output, mqtt.MQTTMessage):
            assert compare_mqtt_msg(output, expected_output)
        else:
            assert output == expected_output

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('reg_result_0', {"middleware_name": "test_middleware", "error": 0},
     True),
    ('reg_result_1', {"middleware_name": "test_middleware", "error": -1},
     False),
    ('reg_result_2', {"middleware_name": "test_middleware", "error": -4},
     True),
    ('reg_result_3', {"middleware_name": "test_middleware", "error": -5},
     False),
    ('reg_result_4', {"middleware_name": "test_middleware", "error": -7},
     False),
    ('reg_result_5', {"middleware_name": "test_middleware", "error": -11},
     False)
])
def test_register_result_handle(test_id: str, input: dict, expected_output: bool, big_thing: MXBigThing):

    def setup(input, big_thing: MXBigThing) -> Tuple[MXBigThing, dict]:
        msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (MXBigThing.DEFAULT_NAME),
                                  payload=input)
        return big_thing, msg

    def task(big_thing: MXBigThing, msg: mqtt.MQTTMessage) -> MXTag:
        result = big_thing._handle_MT_RESULT_REGISTER(msg)
        return result

    big_thing, msg = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing, msg)
    else:
        output = task(big_thing, msg)
        assert output == expected_output

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('reg_result_topic_0', 'MT/RESULT/REGISTER/%s',
     True),
    ('reg_result_topic_1', 'M3/RESULT/REGISTER/%s',
     False),
    ('reg_result_topic_2', 'MT/R3SULT/REGISTER/%s',
     False),
    ('reg_result_topic_3', 'MT/RESULT/R3GISTER/%s',
     False),
    ('reg_result_topic_4', 'MT/RESULT/REGISTER/diff_%s',
     False)
])
def test_register_result_topic_handle(test_id: str, input: str, expected_output: bool, big_thing: MXBigThing):

    def setup(input, big_thing: MXBigThing) -> Tuple[MXBigThing, dict]:
        msg = encode_MQTT_message(topic=input % (MXBigThing.DEFAULT_NAME),
                                  payload={"middleware_name": "test_middleware", "error": 0})
        return big_thing, msg

    def task(big_thing: MXBigThing, msg: mqtt.MQTTMessage) -> MXTag:
        result = big_thing._handle_mqtt_message(msg)
        return result

    big_thing, msg = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing, msg)
    else:
        output = task(big_thing, msg)
        assert output == expected_output

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('reg_result_payload_0', {"middleware_name": "test_middleware", "error": 0},
     True),
    ('reg_result_payload_1', {"middleware_na": "test_middleware", "error": 0},
     KeyError()),
    ('reg_result_payload_2', {"middleware_name": "test_middleware", "err": 0},
     KeyError())
])
def test_register_result_payload_handle(test_id: str, input: dict, expected_output: bool, big_thing: MXBigThing):

    def setup(input, big_thing: MXBigThing) -> Tuple[MXBigThing, dict]:
        msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_REGISTER.value % (MXBigThing.DEFAULT_NAME),
                                  payload=input)
        return big_thing, msg

    def task(big_thing: MXBigThing, msg: mqtt.MQTTMessage) -> MXTag:
        result = big_thing._handle_MT_RESULT_REGISTER(msg)
        return result

    big_thing, msg = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing, msg)
    else:
        output = task(big_thing, msg)
        assert output == expected_output


# TODO: complete this test
# @pytest.mark.parametrize('test_id, big_thing', reg_retry_test_input)
# def test_register_retry(test_id: str, big_thing: MXBigThing):
#     # big_thing.run()
#     pass


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
