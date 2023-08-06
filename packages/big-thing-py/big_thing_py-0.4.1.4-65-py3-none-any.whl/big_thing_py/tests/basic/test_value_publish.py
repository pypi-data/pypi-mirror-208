from big_thing_py.tests.thing_factory import *
from big_thing_py.tests.conftest import PARAMETRIZE_STRING, compare_mqtt_msg, compare_mqtt_msg_list
import pytest


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('value_publish_gen_0', dict(big_thing=MXBigThing(), value=MXValue(func=func_no_argument_with_return_1, tag_list=[MXTag('tag1')], type=MXType.INTEGER, bound=(0, 100), cycle=10)),
     encode_MQTT_message(topic=MXProtocolType.Base.TM_VALUE_PUBLISH.value % (f'{MXBigThing.DEFAULT_NAME}', 'func_no_argument_with_return_1'),
                         payload=dict(type='int', value=None)))
])
def test_generate_value_publish(test_id: str, input: dict, expected_output, big_thing: MXBigThing):

    def setup(input, big_thing: MXBigThing) -> Tuple[MXBigThing, MXValue]:
        value: MXValue = input['value']
        return big_thing, value

    def task(big_thing: MXBigThing, value: MXValue) -> mqtt.MQTTMessage:
        value_pub_msg = big_thing._generate_value_publish_message(value)
        return value_pub_msg

    big_thing, value = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing, value)
    else:
        output = task(big_thing, value)
        assert compare_mqtt_msg(output, expected_output)


####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('value_update_0', func_no_argument_with_increase_int,
     2),
    ('value_update_1', func_no_argument_with_return_1,
     None)
])
def test_value_publish_update(test_id: str, input: Callable, expected_output):

    def setup(input) -> Tuple[MXBigThing, MXValue]:
        value = MXValue(func=func_no_argument_with_return_1, tag_list=[MXTag('tag1')], type=MXType.INTEGER, bound=(0, 100), cycle=10)
        value.set_func(input)
        return value

    def task(value: MXValue) -> Union[int, float, str, bool]:
        value.update()
        curr_val = value.update()
        return curr_val

    value = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(value)
    else:
        output = task(value)
        assert output == expected_output

####################################################################################################################################


@ pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('value_publish_binary_result_0', dict(value_name='func_no_argument_with_return_binary'),
     True),
    ('value_publish_binary_result_1', dict(value_name='not_exist_value'),
     False)
])
def test_binary_result_handle(test_id: str, input: str, expected_output, big_thing: MXBigThing):

    def setup(input, big_thing: MXBigThing) -> Tuple[MXBigThing, mqtt.MQTTMessage]:
        binary_value = MXValue(func=func_no_argument_with_return_binary, tag_list=[
                               MXTag('tag1')], type=MXType.BINARY, bound=(0, 1024 * 1000), cycle=10)
        big_thing.add_service(binary_value)
        binary_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_BINARY_VALUE.value % (MXBigThing.DEFAULT_NAME),
                                                payload=input)
        return big_thing, binary_result_msg

    def task(big_thing: MXBigThing, binary_result_msg: mqtt.MQTTMessage) -> Union[int, float, str, bool]:
        result = big_thing._handle_MT_RESULT_BINARY_VALUE(binary_result_msg)
        return result

    big_thing, binary_result_msg = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing, binary_result_msg)
    else:
        output = task(big_thing, binary_result_msg)
        assert output == expected_output

####################################################################################################################################


@ pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('value_publish_binary_result_topic_0', 'MT/RESULT/BINARY_VALUE/%s',
     True),
    ('value_publish_binary_result_topic_1', 'M3/RESULT/BINARY_VALUE/%s',
     False),
    ('value_publish_binary_result_topic_2', 'MT/R3SULT/BINARY_VALUE/%s',
     False),
    ('value_publish_binary_result_topic_3', 'MT/RESULT/BINARY_VALU3/%s',
     False),
    ('value_publish_binary_result_topic_4', 'MT/RESULT/BINARY_VALUE/diff_%s',
     False)
])
def test_binary_result_topic_handle(test_id: str, input: str, expected_output, big_thing: MXBigThing):

    def setup(input, big_thing: MXBigThing) -> Tuple[MXBigThing, mqtt.MQTTMessage]:
        binary_value = MXValue(func=func_no_argument_with_return_binary, tag_list=[MXTag('tag1')], type=MXType.BINARY, bound=(0, 1024 * 1000), cycle=10)
        big_thing.add_service(binary_value)
        binary_result_msg = encode_MQTT_message(topic=input % (MXBigThing.DEFAULT_NAME),
                                                payload={'value_name': 'func_no_argument_with_return_binary'})
        return big_thing, binary_result_msg

    def task(big_thing: MXBigThing, binary_result_msg: mqtt.MQTTMessage) -> Union[int, float, str, bool]:
        result = big_thing._handle_mqtt_message(binary_result_msg)
        return result

    big_thing, binary_result_msg = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing, binary_result_msg)
    else:
        output = task(big_thing, binary_result_msg)
        assert output == expected_output

####################################################################################################################################


@ pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('value_publish_binary_result_payload_0', {"value_name": "func_no_argument_with_return_binary"},
     True),
    ('value_publish_binary_result_payload_1', {"value_na": "func_no_argument_with_return_binary"},
     KeyError())
])
def test_binary_result_payload_handle(test_id: str, input: str, expected_output, big_thing: MXBigThing):

    def setup(input, big_thing: MXBigThing) -> Tuple[MXBigThing, mqtt.MQTTMessage]:
        binary_value = MXValue(func=func_no_argument_with_return_binary, tag_list=[MXTag('tag1')], type=MXType.BINARY, bound=(0, 1024 * 1000), cycle=10)
        big_thing.add_service(binary_value)
        binary_result_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_BINARY_VALUE.value % (MXBigThing.DEFAULT_NAME),
                                                payload=input)
        return big_thing, binary_result_msg

    def task(big_thing: MXBigThing, binary_result_msg: mqtt.MQTTMessage) -> Union[int, float, str, bool]:
        result = big_thing._handle_MT_RESULT_BINARY_VALUE(binary_result_msg)
        return result

    big_thing, binary_result_msg = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing, binary_result_msg)
    else:
        output = task(big_thing, binary_result_msg)
        assert output == expected_output

####################################################################################################################################


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
