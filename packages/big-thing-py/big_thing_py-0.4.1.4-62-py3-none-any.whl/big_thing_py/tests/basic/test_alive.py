from big_thing_py.tests.thing_factory import *
from big_thing_py.tests.conftest import PARAMETRIZE_STRING, compare_mqtt_msg, compare_mqtt_msg_list
import pytest


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('alive_gen_0', dict(big_thing=MXBigThing(), args=dict()),
     encode_MQTT_message(topic=MXProtocolType.Base.TM_ALIVE.value % (MXBigThing.DEFAULT_NAME),
                         payload=EMPTY_JSON)),
])
def test_generate_alive_message(test_id: str, input: Dict[str, Union[MXBigThing, dict]], expected_output: mqtt.MQTTMessage):

    def setup(input: Dict[str, Union[MXBigThing, dict]]) -> Tuple[dict, MXBigThing]:
        args = input['args']
        big_thing = input['big_thing']

        return args, big_thing

    def task(args: dict, big_thing: MXBigThing) -> mqtt.MQTTMessage:
        alive_msg = big_thing._generate_alive_message(**args)
        return alive_msg

    args, big_thing = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(args, big_thing)
    else:
        output = task(args, big_thing)
        assert compare_mqtt_msg(output, expected_output)

####################################################################################################################################


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
