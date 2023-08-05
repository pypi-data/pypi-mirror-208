from big_thing_py.tests.thing_factory import *
from big_thing_py.tests.conftest import PARAMETRIZE_STRING, compare_mqtt_msg, compare_mqtt_msg_list
import pytest

unreg_gen_1_thing = BigThingFactory().create_default_thing()


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('unreg_gen_0', MXBigThing(),
     encode_MQTT_message(MXProtocolType.Base.TM_UNREGISTER.value % (MXBigThing.DEFAULT_NAME), EMPTY_JSON))
])
def test_generate_unregister_message(test_id: str, input: MXBigThing, expected_output):

    def setup(input) -> MXBigThing:
        big_thing: MXBigThing = input
        return big_thing

    def task(big_thing: MXBigThing) -> mqtt.MQTTMessage:
        msg = big_thing._generate_unregister_message()
        return msg

    big_thing = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing)
    else:
        output = task(big_thing)
        assert compare_mqtt_msg(output, expected_output)

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('unreg_result_0', {'error': 0},
     True),
    ('unreg_result_1', {'error': -1},
     False)
])
def test_unregister_result_handle(test_id: str, input: str, expected_output: Union[dict, bool], big_thing: MXBigThing):

    def setup(input, big_thing: MXBigThing) -> Tuple[MXBigThing, mqtt.MQTTMessage]:
        msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_UNREGISTER.value % (MXBigThing.DEFAULT_NAME),
                                  payload=input)
        return big_thing, msg

    def task(big_thing: MXBigThing, msg: mqtt.MQTTMessage) -> mqtt.MQTTMessage:
        unreg_msg = big_thing._handle_MT_RESULT_UNREGISTER(msg)
        return unreg_msg

    big_thing, msg = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing, msg)
    else:
        output = task(big_thing, msg)
        assert output == expected_output

####################################################################################################################################


@pytest.mark.parametrize('test_id, input, expected_output', [
    ('unreg_result_topic_0', 'MT/RESULT/UNREGISTER/%s',
     True),
    ('unreg_result_topic_1', 'M3/RESULT/UNREGISTER/%s',
     False),
    ('unreg_result_topic_2', 'MT/R3SULT/UNREGISTER/%s',
     False),
    ('unreg_result_topic_3', 'MT/RESULT/UR3GISTER/%s',
     False),
    ('unreg_result_topic_4', 'MT/RESULT/UNREGISTER/diff_%s',
     False)
])
def test_unregister_result_topic_handle(test_id: str, input, expected_output, big_thing: MXBigThing):

    def setup(input, big_thing: MXBigThing) -> MXBigThing:
        unreg_msg = encode_MQTT_message(topic=input % (MXBigThing.DEFAULT_NAME),
                                        payload={'error': 0})
        return big_thing, unreg_msg

    def task(big_thing: MXBigThing, msg: mqtt.MQTTMessage) -> mqtt.MQTTMessage:
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


@pytest.mark.parametrize('test_id, input, expected_output', [
    ('unreg_result_payload_0', {'error': 0},
     True),
    ('unreg_result_payload_1', {'err': 0},
     KeyError())
])
def test_unregister_result_payload_handle(test_id: str, input, expected_output, big_thing: MXBigThing):

    def setup(input, big_thing: MXBigThing) -> MXBigThing:
        unreg_msg = encode_MQTT_message(topic=MXProtocolType.Base.MT_RESULT_UNREGISTER.value % (MXBigThing.DEFAULT_NAME),
                                        payload=input)
        return big_thing, unreg_msg

    def task(big_thing: MXBigThing, msg: mqtt.MQTTMessage) -> mqtt.MQTTMessage:
        result = big_thing._handle_MT_RESULT_UNREGISTER(msg)
        return result

    big_thing, msg = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing, msg)
    else:
        output = task(big_thing, msg)
        assert output == expected_output


####################################################################################################################################


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
