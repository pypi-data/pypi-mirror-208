from big_thing_py.tests.thing_factory import *
from big_thing_py.tests.conftest import PARAMETRIZE_STRING, compare_mqtt_msg, compare_mqtt_msg_list
import pytest


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('function_execute_0', dict(msg=encode_MQTT_message(topic='MT/EXECUTE/function1/default_thing',
                                                        payload={
                                                            'scenario': 'test_scenario',
                                                            'arguments': [
                                                                {
                                                                    'order': 0,
                                                                    'value': 100
                                                                },
                                                                {
                                                                    'order': 1,
                                                                    'value': 123.4
                                                                },
                                                                {
                                                                    'order': 2,
                                                                    'value': 'test_string'
                                                                },
                                                                {
                                                                    'order': 3,
                                                                    'value': True
                                                                },
                                                            ]
                                                        }),
                                function=MXFunction(name='function1', func=func_with_argument_with_return_1, tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
                                                    arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                              MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                              MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                              MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER)),
        MXErrorCode.NO_ERROR),
    ('function_execute_1', dict(msg=encode_MQTT_message(topic='MT/EXECUTE/function1/default_thing/test_middleware/test_request_ID',
                                                        payload={
                                                            'scenario': 'test_scenario',
                                                            'arguments': [
                                                                {
                                                                    'order': 0,
                                                                    'value': 100
                                                                },
                                                                {
                                                                    'order': 1,
                                                                    'value': 123.4
                                                                },
                                                                {
                                                                    'order': 2,
                                                                    'value': 'test_string'
                                                                },
                                                                {
                                                                    'order': 3,
                                                                    'value': True
                                                                },
                                                            ]
                                                        }),
                                function=MXFunction(name='function1', func=func_with_argument_with_return_1, tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
                                                    arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                              MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                              MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                              MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER)),
     MXErrorCode.NO_ERROR),
    ('function_execute_2', dict(msg=encode_MQTT_message(topic='MT/EXECUTE/function1/default_thing',
                                                        payload={
                                                            'scenario': 'test_scenario',
                                                            'arguments': [
                                                                {
                                                                    'order': 0,
                                                                    'value': 100
                                                                },
                                                                {
                                                                    'order': 1,
                                                                    'value': 123.4
                                                                }
                                                            ]
                                                        }),
                                function=MXFunction(name='function1', func=func_with_argument_with_return_1, tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
                                                    arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                                              MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                                              MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                                              MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER)),
     MXErrorCode.FAIL),
    ('function_execute_3', dict(msg=encode_MQTT_message(topic='MT/EXECUTE/timeout_function1/default_thing',
                                                        payload={
                                                            'scenario': 'test_scenario',
                                                            'arguments': [
                                                                {
                                                                    'order': 0,
                                                                    'value': 3
                                                                }
                                                            ]
                                                        }),
                                function=MXFunction(name='timeout_function1', func=func_with_timeout_argument_with_return_1, tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
                                                    arg_list=[MXArgument(name='timeout', type=MXType.DOUBLE, bound=(0, 1000000))], return_type=MXType.INTEGER, timeout=1)),
     MXErrorCode.TIMEOUT),
])
def test_function_execute(test_id: str, input: Dict[str, Union[mqtt.MQTTMessage, MXFunction]], expected_output: MXErrorCode, big_thing: MXBigThing):

    def setup(input: Dict[str, Union[mqtt.MQTTMessage, MXFunction]], big_thing: MXBigThing) -> Tuple[MXFunction, MXExecuteMessage]:
        msg = input['msg']
        function = input['function']

        execute_msg = MXExecuteMessage(msg)
        function = big_thing.add_service(function).get_function_list()[0]
        return function, execute_msg

    def task(function: MXFunction, execute_msg: MXExecuteMessage) -> MXErrorCode:
        function.start_execute_thread(execute_msg)

        while function._running:
            time.sleep(0.05)

        result_msg = function._publish_queue.get()
        error = MXErrorCode.get(decode_MQTT_message(result_msg)[1]['error'])
        return error

    function, execute_msg = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(function, execute_msg)
    else:
        output = task(function, execute_msg)
        assert output == expected_output

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('function_execute_topic_0', 'MT/EXECUTE/function1/%s',
     MXErrorCode.NO_ERROR),
    ('function_execute_topic_1', 'M3/EXECUTE/function1/%s',
     False),
    ('function_execute_topic_2', 'MT/EX3CUTE/function1/%s',
     False),
    ('function_execute_topic_3', 'MT/EXECUTE/diff_function1/%s',
     False),
    ('function_execute_topic_4', 'MT/EXECUTE/function1/diff_%s',
     False),
    ('function_execute_topic_5', 'MT/EXECUTE/function1/%s/test_middleware/test_request_ID',
     MXErrorCode.NO_ERROR),
    ('function_execute_topic_6', 'MT/EXECUTE/function1/%s/test_middleware',
     False),
    ('function_execute_topic_7', 'MT/EXECUTE/function1/%s/test_middleware/',
     False),
])
def test_function_execute_topic_handle(test_id: str, input: str, expected_output: int, big_thing: MXBigThing):

    def setup(input: str, big_thing: MXBigThing) -> Tuple[MXBigThing, MXFunction, MXExecuteMessage]:
        function = MXFunction(name='function1', func=func_with_argument_with_return_1, tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
                              arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                        MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                        MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                        MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER)
        big_thing.add_service(function)

        execute_msg = encode_MQTT_message(topic=input % (big_thing.get_name()),
                                          payload={'scenario': 'test_scenario',
                                                   'arguments': [{'order': 0, 'value': 100}, {'order': 1, 'value': 123.4}, {'order': 2, 'value': 'test_string'}, {'order': 3, 'value': True}]})
        return big_thing, function, execute_msg

    def task(big_thing: MXBigThing, function: MXFunction, execute_msg: MXExecuteMessage) -> List[MXService]:
        result = big_thing._handle_mqtt_message(execute_msg)
        if result == False:
            return result

        while function._running:
            time.sleep(0.05)

        result_msg = function._publish_queue.get()
        error = MXErrorCode.get(decode_MQTT_message(result_msg)[1]['error'])
        return error

    big_thing, function, execute_msg = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing, function, execute_msg)
    else:
        output = task(big_thing, function, execute_msg)
        assert output == expected_output


####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('function_execute_payload_0', dict(payload={
        "scenario": "test_scenario",
        "arguments": [
            {
                "order": 0,
                "value": 100
            },
            {
                "order": 1,
                "value": 123.4
            },
            {
                "order": 2,
                "value": "test_string"
            },
            {
                "order": 3,
                "value": True
            },
        ]
    }),
        MXErrorCode.NO_ERROR),
    ('function_execute_payload_1', dict(payload={
        "scenar": "test_scenario",
        "arguments": [
            {
                "order": 0,
                "value": 100
            },
            {
                "order": 1,
                "value": 123.4
            },
            {
                "order": 2,
                "value": "test_string"
            },
            {
                "order": 3,
                "value": True
            },
        ]
    }),
        False),
    ('function_execute_payload_2', dict(payload={
        "scenario": "",
        "arguments": [
            {
                "order": 0,
                "value": 100
            },
            {
                "order": 1,
                "value": 123.4
            },
            {
                "order": 2,
                "value": "test_string"
            },
            {
                "order": 3,
                "value": True
            },
        ]
    }),
        False),
    ('function_execute_payload_3', dict(payload={
        "scenario": "test_scenario",
        "argumen": [
            {
                "order": 0,
                "value": 100
            },
            {
                "order": 1,
                "value": 123.4
            },
            {
                "order": 2,
                "value": "test_string"
            },
            {
                "order": 3,
                "value": True
            },
        ]
    }),
        False),
    ('function_execute_payload_4', dict(payload={
        "scenario": "test_scenario",
        "arguments": [
            {
                "ord": 0,
                "value": 100
            },
            {
                "order": 1,
                "value": 123.4
            },
            {
                "order": 2,
                "value": "test_string"
            },
            {
                "order": 3,
                "value": True
            },
        ]
    }),
        False),
    ('function_execute_payload_5', dict(payload={
        "scenario": "test_scenario",
        "arguments": [
            {
                "order": "0",
                "value": 100
            },
            {
                "order": "1",
                "value": 123.4
            },
            {
                "order": "2",
                "value": "test_string"
            },
            {
                "order": "3",
                "value": True
            },
        ]
    }),
        False),
    ('function_execute_payload_6', dict(payload={
        "scenario": "test_scenario",
        "arguments": [
            {
                "order": 0,
                "val": 100
            },
            {
                "order": 1,
                "value": 123.4
            },
            {
                "order": 2,
                "value": "test_string"
            },
            {
                "order": 3,
                "value": True
            },
        ]
    }),
        False),
    ('function_execute_payload_7', dict(payload={
        "scenario": "test_scenario",
        "arguments": [
            {
                "order": 0,
                "value": 101.1
            },
            {
                "order": 1,
                "value": 123
            },
            {
                "order": 2,
                "value": "test_string"
            },
            {
                "order": 3,
                "value": True
            },
        ]
    }),
        MXErrorCode.NO_ERROR),
    ('function_execute_payload_8', dict(payload={
        "scenario": "test_scenario",
        "arguments": [
            {
                "order": 0,
                "value": "100"
            },
            {
                "order": 1,
                "value": 123.4
            },
            {
                "order": 2,
                "value": "test_string"
            },
            {
                "order": 3,
                "value": True
            },
        ]
    }),
        False),
    ('function_execute_payload_9', dict(payload={
        "scenario": "test_scenario",
        "arguments": [
            {
                "order": 0,
                "value": 100
            },
            {
                "order": 1,
                "value": "123.4"
            },
            {
                "order": 2,
                "value": "test_string"
            },
            {
                "order": 3,
                "value": True
            },
        ]
    }),
        False),
    ('function_execute_payload_10', dict(payload={
        "scenario": "test_scenario",
        "arguments": [
            {
                "order": 0,
                "value": 100
            },
            {
                "order": 1,
                "value": 123.4
            },
            {
                "order": 2,
                "value": "test_string"
            },
            {
                "order": 3,
                "value": "True"
            },
        ]
    }),
        False),
    ('function_execute_payload_11', dict(payload={
        "scenario": "test_scenario",
        "arguments": [
            {
                "order": 0,
                "value": 100
            },
            {
                "order": 1,
                "value": 123.4
            },
            {
                "order": 2,
                "value": "test_string"
            },
            {
                "order": 3,
                "value": 1
            },
        ]
    }),
        False),
    ('function_execute_payload_12', dict(payload={
        "scenario": "test_scenario",
        "arguments": [
            {
                "order": 0,
                "value": 100
            },
            {
                "order": 1,
                "value": 123.4
            },
            {
                "order": 2,
                "value": "test_string"
            },
            {
                "order": 3,
                "value": 1.0
            },
        ]
    }),
        False),
])
def test_function_execute_payload_handle(test_id: str, input: Dict[str, dict], expected_output: Union[MXErrorCode, bool], big_thing: MXBigThing):

    def setup(input: str, big_thing: MXBigThing) -> Tuple[MXBigThing, MXFunction, MXExecuteMessage]:
        function = MXFunction(name='function1', func=func_with_argument_with_return_1, tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
                              arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                        MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                        MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                        MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER)
        function = big_thing.add_service(function).get_function_list()[0]

        execute_msg = encode_MQTT_message(topic=(MXProtocolType.Base.MT_EXECUTE.value % (function.get_name(), big_thing.get_name(), '', '')).rstrip('/'),
                                          payload=input['payload'])

        return big_thing, function, execute_msg

    def task(big_thing: MXBigThing, function: MXFunction, execute_msg: MXExecuteMessage) -> List[MXService]:
        result = big_thing._handle_MT_EXECUTE(execute_msg)
        if result == False:
            return result

        while function._running:
            time.sleep(0.05)

        result_msg = function._publish_queue.get()
        error = MXErrorCode.get(decode_MQTT_message(result_msg)[1]['error'])
        return error

    big_thing, function, execute_msg = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing, function, execute_msg)
    else:
        output = task(big_thing, function, execute_msg)
        assert output == expected_output

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('function_execute_result_gen_0', dict(args=dict(scenario='test_scenario', request_ID=None, error=MXErrorCode.NO_ERROR)),
     encode_MQTT_message(topic=(MXProtocolType.Base.TM_RESULT_EXECUTE.value % ('function1', f'{MXBigThing().get_name()}', '', '')).rstrip('/'),
                         payload={
         "error": 0,
         "scenario": "test_scenario",
         "return_type": "int",
         "return_value": None
     })),
    ('function_execute_result_gen_1', dict(args=dict(scenario='test_scenario', request_ID=None, error=MXErrorCode.FAIL)),
     encode_MQTT_message(topic=(MXProtocolType.Base.TM_RESULT_EXECUTE.value % ('function1', f'{MXBigThing().get_name()}', '', '')).rstrip('/'),
                         payload={
         "error": -1,
         "scenario": "test_scenario",
         "return_type": "int",
         "return_value": None
     })),
    ('function_execute_result_gen_2', dict(args=dict(scenario='test_scenario', request_ID=None, error=MXErrorCode.TIMEOUT)),
     encode_MQTT_message(topic=(MXProtocolType.Base.TM_RESULT_EXECUTE.value % ('function1', f'{MXBigThing().get_name()}', '', '')).rstrip('/'),
                         payload={
         "error": -2,
         "scenario": "test_scenario",
         "return_type": "int",
         "return_value": None
     })),
    ('function_execute_result_gen_3', dict(args=dict(scenario='test_scenario', request_ID=None, error=MXErrorCode.DUPLICATE)),
     encode_MQTT_message(topic=(MXProtocolType.Base.TM_RESULT_EXECUTE.value % ('function1', f'{MXBigThing().get_name()}', '', '')).rstrip('/'),
                         payload={
         "error": -4,
         "scenario": "test_scenario",
         "return_type": "int",
         "return_value": None
     })),
    ('function_execute_result_gen_4', dict(args=dict(scenario='test_scenario', request_ID='test_request_ID', error=MXErrorCode.NO_ERROR)),
     encode_MQTT_message(topic=(MXProtocolType.Base.TM_RESULT_EXECUTE.value % ('function1', f'{MXBigThing().get_name()}', 'test_middleware', 'test_request_ID')).rstrip('/'),
                         payload={
         "error": 0,
         "scenario": "test_scenario",
         "return_type": "int",
         "return_value": None
     })),
])
def test_generate_function_execute_result(test_id: str, input: Dict[str, dict], expected_output: Tuple[str, dict], big_thing: MXBigThing):

    def setup(input: Dict[str, dict], big_thing: MXBigThing) -> Tuple[dict, MXFunction]:
        args: dict = input['args']
        function = MXFunction(name='function1', func=func_with_argument_with_return_1, tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
                              arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                                        MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                                        MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                                        MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))], return_type=MXType.INTEGER)
        function = big_thing.add_service(function).get_function_list()[0]
        function.set_middleware_name('test_middleware')

        return args, function

    def task(args: dict, function: MXFunction) -> MXExecuteResultMessage:
        execute_result_msg = function._generate_execute_result_message(**args)
        return execute_result_msg

    args, function = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(args, function)
    else:
        output = task(args, function)
        assert compare_mqtt_msg(output, expected_output)

####################################################################################################################################


@ pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('function_execute_parallel_0', dict(is_parallel=True,
                                         function1=MXFunction(func=func_no_argument_with_return_1, tag_list=[MXTag('tag1')],
                                                              arg_list=[], return_type=MXType.INTEGER),
                                         execute_msg1={
                                             "scenario": "test_scenario1", "arguments": []},
                                         function2=MXFunction(func=func_with_timeout_argument_with_return_1, tag_list=[MXTag('tag1')],
                                                              arg_list=[MXArgument(name='timeout', type=MXType.DOUBLE, bound=(0, 1000000))], return_type=MXType.INTEGER, timeout=1),
                                         execute_msg2={
                                             "scenario": "test_scenario2", "arguments": [{
                                                 "order": 0,
                                                 "value": 0.5
                                             }]}),
     [(MXErrorCode.NO_ERROR, 1), (MXErrorCode.NO_ERROR, 1), 0.7]),
    ('function_execute_parallel_1', dict(is_parallel=True,
                                         function1=MXFunction(func=func_with_timeout_argument_with_return_1, tag_list=[MXTag('tag1')],
                                                              arg_list=[MXArgument(name='timeout', type=MXType.DOUBLE, bound=(0, 1000000))], return_type=MXType.INTEGER, timeout=1),
                                         execute_msg1={
                                             "scenario": "test_scenario1", "arguments": [{
                                                 "order": 0,
                                                 "value": 0.5
                                             }]},
                                         function2=MXFunction(func=func_with_timeout_argument_with_return_1, tag_list=[MXTag('tag1')],
                                                              arg_list=[MXArgument(name='timeout', type=MXType.DOUBLE, bound=(0, 1000000))], return_type=MXType.INTEGER, timeout=1),
                                         execute_msg2={
                                             "scenario": "test_scenario2", "arguments": [{
                                                 "order": 0,
                                                 "value": 0.5
                                             }]}),
     [(MXErrorCode.NO_ERROR, 1), (MXErrorCode.NO_ERROR, 1), 0.7]),
    ('function_execute_parallel_2', dict(is_parallel=True,
                                         function1=MXFunction(func=func_with_timeout_argument_with_return_1, tag_list=[MXTag('tag1')],
                                                              arg_list=[MXArgument(name='timeout', type=MXType.DOUBLE, bound=(0, 1000000))], return_type=MXType.INTEGER, timeout=1),
                                         execute_msg1={
                                             "scenario": "test_scenario1", "arguments": [{
                                                 "order": 0,
                                                 "value": 0.5
                                             }]},
                                         function2=MXFunction(func=func_with_timeout_argument_with_return_1, tag_list=[MXTag('tag1')],
                                                              arg_list=[MXArgument(name='timeout', type=MXType.DOUBLE, bound=(0, 1000000))], return_type=MXType.INTEGER, timeout=1),
                                         execute_msg2={
                                             "scenario": "test_scenario2", "arguments": [{
                                                 "order": 0,
                                                 "value": 1.5
                                             }]}),
     [(MXErrorCode.NO_ERROR, 1), (MXErrorCode.TIMEOUT, 1), 1.2]),
    ('function_execute_parallel_3', dict(is_parallel=True,
                                         function1=MXFunction(func=func_with_timeout_argument_with_return_1, tag_list=[MXTag('tag1')],
                                                              arg_list=[MXArgument(name='timeout', type=MXType.DOUBLE, bound=(0, 1000000))], return_type=MXType.INTEGER, timeout=1),
                                         execute_msg1={
                                             "scenario": "test_scenario1", "arguments": [{
                                                 "order": 0,
                                                 "value": 0.5
                                             }]},
                                         function2=MXFunction(func=func_with_timeout_argument_with_return_1, tag_list=[MXTag('tag1')],
                                                              arg_list=[MXArgument(name='timeout', type=MXType.DOUBLE, bound=(0, 1000000))], return_type=MXType.INTEGER, timeout=1),
                                         execute_msg2={
                                             "scenario": "test_scenario1", "arguments": [{
                                                 "order": 0,
                                                 "value": 0.5
                                             }]}),
     [(MXErrorCode.DUPLICATE, None), (MXErrorCode.NO_ERROR, 1), 0.7]),
    ('function_execute_parallel_4', dict(is_parallel=False,
                                         function1=MXFunction(func=func_with_timeout_argument_with_return_1, tag_list=[MXTag('tag1')],
                                                              arg_list=[MXArgument(name='timeout', type=MXType.DOUBLE, bound=(0, 1000000))], return_type=MXType.INTEGER, timeout=1),
                                         execute_msg1={
                                             "scenario": "test_scenario1", "arguments": [{
                                                 "order": 0,
                                                 "value": 0.5
                                             }]},
                                         function2=MXFunction(func=func_with_timeout_argument_with_return_1, tag_list=[MXTag('tag1')],
                                                              arg_list=[MXArgument(name='timeout', type=MXType.DOUBLE, bound=(0, 1000000))], return_type=MXType.INTEGER, timeout=1),
                                         execute_msg2={
                                             "scenario": "test_scenario2", "arguments": [{
                                                 "order": 0,
                                                 "value": 0.5
                                             }]}),
     [(MXErrorCode.FAIL, None), (MXErrorCode.NO_ERROR, 1), 0.7]),
])
def test_function_execute_parallel(test_id: str, input: Dict[str, Union[bool, MXFunction]], expected_output: List[Union[Tuple[MXErrorCode, int], float]]):

    def setup(input) -> Tuple[MXBigThing, MXFunction, MXFunction, mqtt.MQTTMessage, mqtt.MQTTMessage]:
        is_parallel = input['is_parallel']
        function1 = input['function1']
        function2 = input['function2']
        execute_msg1 = input['execute_msg1']
        execute_msg2 = input['execute_msg2']
        big_thing = MXBigThing(is_parallel=is_parallel,
                               service_list=[function1, function2])
        function1 = big_thing.get_function_list()[0]
        function2 = big_thing.get_function_list()[1]
        msg1 = encode_MQTT_message(topic=(MXProtocolType.Base.MT_EXECUTE.value % (function1.get_name(), big_thing.get_name(), '', '')).rstrip('/'),
                                   payload=execute_msg1)
        msg2 = encode_MQTT_message(topic=(MXProtocolType.Base.MT_EXECUTE.value % (function2.get_name(), big_thing.get_name(), '', '')).rstrip('/'),
                                   payload=execute_msg2)

        return big_thing, function1, function2, msg1, msg2

    def task(big_thing: MXBigThing, function1: MXFunction, function2: MXFunction, msg1: mqtt.MQTTMessage, msg2: mqtt.MQTTMessage) -> MXExecuteResultMessage:
        start_time = get_current_time()
        big_thing._handle_MT_EXECUTE(msg1)
        time.sleep(0.05)
        big_thing._handle_MT_EXECUTE(msg2)

        while function1._running or function2._running:
            time.sleep(0.05)
        result_msg1 = function1._publish_queue.get()
        result_msg2 = function2._publish_queue.get()
        end_time = get_current_time()

        error1 = MXErrorCode.get(decode_MQTT_message(result_msg1)[1]['error'])
        error2 = MXErrorCode.get(decode_MQTT_message(result_msg2)[1]['error'])
        value1 = decode_MQTT_message(result_msg1)[1]['return_value']
        value2 = decode_MQTT_message(result_msg2)[1]['return_value']

        return (end_time - start_time), [(error1, value1), (error2, value2)]

    big_thing, function1, function2, msg1, msg2 = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing, function1, function2, msg1, msg2)
    else:
        output = task(big_thing, function1, function2, msg1, msg2)
        assert output[0] < expected_output[2]
        assert output[1] == expected_output[:2]


####################################################################################################################################


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
