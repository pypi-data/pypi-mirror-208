from big_thing_py.tests.thing_factory import *
from big_thing_py.tests.conftest import PARAMETRIZE_STRING
import pytest
import subprocess


def set_ssl_config(mqtt_client: MXClient, ssl_ca_path: str):
    try:
        mqtt_client.tls_set(
            ca_certs=f'{ssl_ca_path}/ca.crt',
            certfile=f'{ssl_ca_path}/client.crt',
            keyfile=f'{ssl_ca_path}/client.key',
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS_CLIENT)
        mqtt_client.tls_insecure_set(True)
    except ValueError as e:
        MXLOG_DEBUG('SSL/TLS has already been configured.', 'yellow')


####################################################################################################################################

recv_queue__test_mqtt_publish = Queue()


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('mqtt_publish_1', dict(msg=encode_MQTT_message(topic='test_topic',
                                                    payload='test_payload')),
     'test_payload'),
])
@pytest.mark.usefixtures('run_mosquitto')
def test_mqtt_publish(test_id: str, input: Dict[str, dict], expected_output: MXTag):

    def mosquitto_sub_thread_func(topic):
        result = subprocess.run(f'mosquitto_sub -t {topic} -C 1', shell=True, stdout=subprocess.PIPE)
        if result.returncode == 0:
            recv_queue__test_mqtt_publish.put(result.stdout.decode().strip())
        else:
            recv_queue__test_mqtt_publish.put(False)

    def setup(input) -> str:
        time.sleep(0.5)

        mqtt_client = MXClient()
        msg = input['msg']
        mqtt_client.connect('127.0.0.1', 1883)
        return mqtt_client, msg

    def task(mqtt_client: MXClient, msg):
        topic, payload, _ = decode_MQTT_message(msg)
        mosquitto_sub_thread = MXThread(target=mosquitto_sub_thread_func, args=(topic, ))
        mosquitto_sub_thread.start()

        time.sleep(0.5)

        mqtt_client.publish(topic, payload)
        mosquitto_sub_thread.join()
        result = recv_queue__test_mqtt_publish.get()
        return result

    mqtt_client, msg = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(mqtt_client, msg)
    else:
        output = task(mqtt_client, msg)
        assert output == expected_output

####################################################################################################################################


recv_queue__test_mqtt_subscribe = Queue()


def on_message(client: MXClient, userdata, msg: mqtt.MQTTMessage):
    topic, payload, _ = decode_MQTT_message(msg)
    recv_queue__test_mqtt_subscribe.put(payload)


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('mqtt_subscribe_1', dict(msg=encode_MQTT_message(topic='test_topic',
                                                      payload='test_payload')),
     'test_payload'),
])
@pytest.mark.usefixtures('run_mosquitto')
def test_mqtt_subscribe(test_id: str, input: Dict[str, dict], expected_output: MXTag):

    def setup(input) -> str:
        time.sleep(0.5)

        mqtt_client = MXClient()
        msg = input['msg']
        mqtt_client.on_message = on_message

        mqtt_client.connect('127.0.0.1', 1883)
        mqtt_client.loop_start()

        return mqtt_client, msg

    def task(mqtt_client: MXClient, msg):
        topic, payload, _ = decode_MQTT_message(msg)
        mqtt_client.subscribe(topic)

        time.sleep(0.5)

        subprocess.run(f'mosquitto_pub -t {topic} -m {payload}', shell=True, stdout=subprocess.PIPE)
        result = recv_queue__test_mqtt_subscribe.get()
        return result

    mqtt_client, msg = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(mqtt_client, msg)
    else:
        output = task(mqtt_client, msg)
        assert output == expected_output


####################################################################################################################################


recv_queue__test_mqtt_ssl_publish = Queue()


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('mqtt_ssl_publish_1', dict(msg=encode_MQTT_message(topic='test_topic',
                                                        payload='test_payload')),
     'test_payload'),
])
@pytest.mark.skipif(sys.platform == 'darwin', reason="run_ssl_mosquitto is not working on MacOS.")
@pytest.mark.usefixtures('install_CA')
@pytest.mark.usefixtures('run_ssl_mosquitto')
def test_mqtt_ssl_publish(test_id: str, input: Dict[str, dict], expected_output: MXTag):

    def mosquitto_sub_thread_func(topic):
        result = subprocess.run(f'mosquitto_sub \
            --cafile {get_project_root()}/res/CA/ca.crt \
            --cert {get_project_root()}/res/CA/client.crt \
            --key {get_project_root()}/res/CA/client.key -h 127.0.0.1 -p 8883 -t {topic} -C 1', shell=True, stdout=subprocess.PIPE)
        if result.returncode == 0:
            recv_queue__test_mqtt_ssl_publish.put(result.stdout.decode().strip())
        else:
            recv_queue__test_mqtt_ssl_publish.put(False)

    def setup(input) -> str:
        time.sleep(0.5)

        mqtt_client = MXClient()
        msg = input['msg']
        set_ssl_config(mqtt_client, ssl_ca_path=f'{get_project_root()}/res/CA')
        mqtt_client.connect('127.0.0.1', 8883)
        return mqtt_client, msg

    def task(mqtt_client: MXClient, msg):
        topic, payload, _ = decode_MQTT_message(msg)
        mosquitto_sub_thread = MXThread(target=mosquitto_sub_thread_func, args=(topic, ))
        mosquitto_sub_thread.start()

        time.sleep(0.5)

        mqtt_client.publish(topic, payload)
        mosquitto_sub_thread.join()
        result = recv_queue__test_mqtt_ssl_publish.get()
        return result

    mqtt_client, msg = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(mqtt_client, msg)
    else:
        output = task(mqtt_client, msg)
        assert output == expected_output

####################################################################################################################################


recv_queue__test_mqtt_ssl_subscribe = Queue()


def on_message_ssl(client: MXClient, userdata, msg: mqtt.MQTTMessage):
    topic, payload, _ = decode_MQTT_message(msg)
    recv_queue__test_mqtt_ssl_subscribe.put(payload)


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('mqtt_ssl_subscribe_1', dict(msg=encode_MQTT_message(topic='test_topic',
                                                          payload='test_payload')),
     'test_payload'),
])
@pytest.mark.skipif(sys.platform == 'darwin', reason="run_ssl_mosquitto is not working on MacOS.")
@pytest.mark.usefixtures('install_CA')
@pytest.mark.usefixtures('run_ssl_mosquitto')
def test_mqtt_ssl_subscribe(test_id: str, input: Dict[str, dict], expected_output: MXTag):

    def setup(input) -> str:
        time.sleep(0.5)

        mqtt_client = MXClient()
        msg = input['msg']
        mqtt_client.on_message = on_message_ssl
        set_ssl_config(mqtt_client, ssl_ca_path=f'{get_project_root()}/res/CA')
        mqtt_client.connect('127.0.0.1', 8883)
        mqtt_client.loop_start()

        return mqtt_client, msg

    def task(mqtt_client: MXClient, msg):
        topic, payload, _ = decode_MQTT_message(msg)
        mqtt_client.subscribe(topic)

        time.sleep(0.5)

        subprocess.run(f'mosquitto_pub \
            --cafile {get_project_root()}/res/CA/ca.crt \
            --cert {get_project_root()}/res/CA/client.crt \
            --key {get_project_root()}/res/CA/client.key -h 127.0.0.1 -p 8883 -t {topic} -m {payload}', shell=True, stdout=subprocess.PIPE)
        result = recv_queue__test_mqtt_ssl_subscribe.get()
        return result

    mqtt_client, msg = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(mqtt_client, msg)
    else:
        output = task(mqtt_client, msg)
        assert output == expected_output

####################################################################################################################################


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
