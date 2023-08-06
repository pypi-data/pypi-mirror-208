from big_thing_py.tests.thing_factory import *
from big_thing_py.tests.conftest import PARAMETRIZE_STRING, compare_mqtt_msg, compare_mqtt_msg_list, MXBasicSuperThing
import pytest


service_list_result_input_1 = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_1.json')
service_list_result_input_2 = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_2.json')
service_list_result_input_3 = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_3.json')
service_list_result_input_4 = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_4.json')
service_list_result_input_5 = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_5.json')
service_list_result_input_6 = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_6.json')
service_list_result_input_7 = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_7.json')
service_list_result_input_8 = json_file_read(f'{get_project_root()}/big_thing_py/tests/super/service_list_result_input_8.json')


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('super_refresh_gen_0', dict(super_thing=MXBasicSuperThing()),
     encode_MQTT_message(topic=MXProtocolType.Super.SM_REFRESH.value % (MXBasicSuperThing.DEFAULT_NAME), payload=EMPTY_JSON)),
])
def test_generate_refresh(test_id: str, input: Dict[str, MXSuperThing], expected_output):

    def setup(input) -> MXBasicSuperThing:
        super_thing: MXBasicSuperThing = input['super_thing']
        return super_thing

    def task(super_thing: MXBasicSuperThing):
        return super_thing._generate_super_refresh_message()

    super_thing = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            output = task(super_thing)
    else:
        output = task(super_thing)
        assert compare_mqtt_msg(output, expected_output)

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('super_service_list_result_1', dict(payload=service_list_result_input_1),
     True),
    ('super_service_list_result_2', dict(payload=service_list_result_input_2),
     True),
    ('super_service_list_result_3', dict(payload=service_list_result_input_3),
     True),
    ('super_service_list_result_4', dict(payload=service_list_result_input_4),
     False),
    ('super_service_list_result_5', dict(payload=service_list_result_input_5),
     False),
    ('super_service_list_result_6', dict(payload=service_list_result_input_6),
     False),
    ('super_service_list_result_7', dict(payload=service_list_result_input_7),
     False),
    ('super_service_list_result_8', dict(payload=service_list_result_input_8),
     False),
])
def test_super_service_result_handle(test_id: str, input: Dict[str, dict], expected_output: bool, basic_super_thing: MXSuperThing):

    def setup(input):
        super_thing = basic_super_thing
        service_list_msg = encode_MQTT_message(topic=MXProtocolType.Super.MS_RESULT_SERVICE_LIST.value % (super_thing.get_name()),
                                               payload=input['payload'])
        return super_thing, service_list_msg

    def task(super_thing: MXBasicSuperThing, service_list_msg: mqtt.MQTTMessage):
        result = super_thing._handle_MS_RESULT_SERVICE_LIST(service_list_msg)
        return result

    super_thing, service_list_msg = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            output = task(super_thing, service_list_msg)
    else:
        output = task(super_thing, service_list_msg)
        assert output == expected_output


if __name__ == '__main__':
    pytest.main(['-s', '-v', __file__])
