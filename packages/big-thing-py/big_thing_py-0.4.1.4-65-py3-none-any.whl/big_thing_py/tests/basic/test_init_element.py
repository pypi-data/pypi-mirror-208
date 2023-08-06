from big_thing_py.tests.thing_factory import *
from big_thing_py.tests.conftest import PARAMETRIZE_STRING
import pytest
import pickle


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('init_tag_0',
     dict(args=dict(name='test_tag1')),
     b'\x80\x04\x95>\x00\x00\x00\x00\x00\x00\x00\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94\x8c\x05_name\x94\x8c\ttest_tag1\x94sb.'),
    ('init_tag_1',
     dict(args=dict(name='test_tag_1')),
     b'\x80\x04\x95?\x00\x00\x00\x00\x00\x00\x00\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94\x8c\x05_name\x94\x8c\ntest_tag_1\x94sb.'),
    ('init_tag_2',
     dict(args=dict(name='_test_tag_1')),
     b'\x80\x04\x95@\x00\x00\x00\x00\x00\x00\x00\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94\x8c\x05_name\x94\x8c\x0b_test_tag_1\x94sb.'),
    ('init_tag_3',
     dict(args=dict(name='1_test_tag')),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_tag_4',
     dict(args=dict(name='test-tag')),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_tag_5',
     dict(args=dict(name='test tag')),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_tag_6',
     dict(args=dict(name='')),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_tag_7',
     dict(args=dict()),
     TypeError()),
])
def test_init_tag(test_id, input: Dict[str, dict], expected_output: Union[bytes, Exception]):

    def setup(input) -> str:
        args = input['args']
        return args

    def task(**args: dict) -> MXTag:
        return MXTag(**args)

    args = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(**args)
    else:
        output = task(**args)
        assert pickle.dumps(output) == expected_output

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('init_argument_0',
     dict(args=dict(name='test_argument1', bound=(0, 100), type=MXType.INTEGER)),
     b'\x80\x04\x95\x9a\x00\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x0etest_argument1\x94\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdub.'),
    ('init_argument_1',
     dict(args=dict(bound=(0, 100), type=MXType.INTEGER)),
     TypeError()),
    ('init_argument_2',
     dict(args=dict(name='test_argument_1', bound=(0, 100))),
     TypeError()),
    ('init_argument_3',
     dict(args=dict(name='test_argument_1', type=MXType.INTEGER)),
     TypeError()),
    ('init_argument_4',
     dict(args=dict(name='test_argument1', bound=(0, 100), type=MXType.INTEGER)),
     b'\x80\x04\x95\x9a\x00\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x0etest_argument1\x94\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdub.'),
    ('init_argument_5',
     dict(args=dict(name='test_argument_1', bound=(0, 100), type=MXType.INTEGER)),
     b'\x80\x04\x95\x9b\x00\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x0ftest_argument_1\x94\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdub.'),
    ('init_argument_6',
     dict(args=dict(name='_test_argument_1', bound=(0, 100), type=MXType.INTEGER)),
     b'\x80\x04\x95\x9c\x00\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x10_test_argument_1\x94\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdub.'),
    ('init_argument_7',
     dict(args=dict(name='1_test_argument', bound=(0, 100), type=MXType.INTEGER)),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_argument_8',
     dict(args=dict(name='test-argument', bound=(0, 100), type=MXType.INTEGER)),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_argument_9',
     dict(args=dict(name='test argument', bound=(0, 100), type=MXType.INTEGER)),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_argument_6',
     dict(args=dict(name='', bound=(0, 100), type=MXType.INTEGER)),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_argument_11',
     dict(args=dict(name='test_argument1', bound=(0, 0), type=MXType.INTEGER)),
     MXValueError('bound must be min < max')),
    ('init_argument_12',
     dict(args=dict(name='test_argument1', bound=(0, -100), type=MXType.INTEGER)),
     MXValueError('bound must be min < max')),
    ('init_argument_13',
     dict(args=dict(name='test_argument1', bound=(0, 100), type=MXType.UNDEFINED)),
     MXValueError('type cannot be undefined or void')),
    ('init_argument_14',
     dict(args=dict(name='test_argument1', bound=(0, 100), type=MXType.VOID)),
     MXValueError('type cannot be undefined or void')),
])
def test_init_argument(test_id: str, input: Dict[str, dict], expected_output: Union[MXArgument, Exception]):

    def setup(input) -> str:
        args = input['args']
        return args

    def task(**args: dict):
        return MXArgument(**args)

    args = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(**args)
    else:
        output = task(**args)
        assert pickle.dumps(output) == expected_output

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('init_value_0',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
     b'\x80\x04\x95]\x01\x00\x00\x00\x00\x00\x00\x8c\x17big_thing_py.core.value\x94\x8c\x07MXValue\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x1efunc_no_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kd\x8c\x06_cycle\x94K\n\x8c\x07_format\x94h\x17ub.'),
    ('init_value_1',
     dict(args=dict(
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
        TypeError()),
    ('init_value_2',
     dict(args=dict(
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
        TypeError()),
    ('init_value_3',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         bound=(0, 100),
         cycle=10)),
        TypeError()),
    ('init_value_4',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         cycle=10)),
        TypeError()),
    ('init_value_5',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100))),
        TypeError()),
    ('init_value_6',
     dict(args=dict(
         name='test_value1',
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
     b'\x80\x04\x95J\x01\x00\x00\x00\x00\x00\x00\x8c\x17big_thing_py.core.value\x94\x8c\x07MXValue\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x0btest_value1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kd\x8c\x06_cycle\x94K\n\x8c\x07_format\x94h\x17ub.'),
    ('init_value_7',
     dict(args=dict(
         name='test_value_1',
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
     b'\x80\x04\x95K\x01\x00\x00\x00\x00\x00\x00\x8c\x17big_thing_py.core.value\x94\x8c\x07MXValue\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x0ctest_value_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kd\x8c\x06_cycle\x94K\n\x8c\x07_format\x94h\x17ub.'),
    ('init_value_8',
     dict(args=dict(
         name='_test_value_1',
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
     b'\x80\x04\x95L\x01\x00\x00\x00\x00\x00\x00\x8c\x17big_thing_py.core.value\x94\x8c\x07MXValue\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\r_test_value_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kd\x8c\x06_cycle\x94K\n\x8c\x07_format\x94h\x17ub.'),
    ('init_value_9',
     dict(args=dict(
         name='1_test_value',
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
        MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_value_10',
     dict(args=dict(
         name='test-value',
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
        MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_value_11',
     dict(args=dict(
         name='test value',
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
        MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_value_12',
     dict(args=dict(
         name='',
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
     b'\x80\x04\x95]\x01\x00\x00\x00\x00\x00\x00\x8c\x17big_thing_py.core.value\x94\x8c\x07MXValue\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x1efunc_no_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kd\x8c\x06_cycle\x94K\n\x8c\x07_format\x94h\x17ub.'),
    ('init_value_13',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
        MXValueError('callback function must not have any argument and must return value')),
    ('init_value_14',
     dict(args=dict(
         func=func_with_argument_no_return,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
        MXValueError('callback function must not have any argument and must return value')),
    ('init_value_15',
     dict(args=dict(
         func=None,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
        MXValueError('func must be callable')),
    ('init_value_16',
     dict(args=dict(
         func=10,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
        MXValueError('func must be callable')),
    ('init_value_17',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
        MXValueError('tag_list must contain MXTag object')),
    ('init_value_18',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
     b'\x80\x04\x958\x01\x00\x00\x00\x00\x00\x00\x8c\x17big_thing_py.core.value\x94\x8c\x07MXValue\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x1efunc_no_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sba\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x11\x8c\x10_middleware_name\x94h\x11\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kd\x8c\x06_cycle\x94K\n\x8c\x07_format\x94h\x11ub.'),
    ('init_value_19',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
     b'\x80\x04\x95]\x01\x00\x00\x00\x00\x00\x00\x8c\x17big_thing_py.core.value\x94\x8c\x07MXValue\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x1efunc_no_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kd\x8c\x06_cycle\x94K\n\x8c\x07_format\x94h\x17ub.'),
    ('init_value_20',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10)),
     b'\x80\x04\x95]\x01\x00\x00\x00\x00\x00\x00\x8c\x17big_thing_py.core.value\x94\x8c\x07MXValue\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x1efunc_no_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kd\x8c\x06_cycle\x94K\n\x8c\x07_format\x94h\x17ub.'),
    ('init_value_21',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 0),
         cycle=10)),
        MXValueError('bound must be min < max')),
    ('init_value_22',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, -100),
         cycle=10)),
        MXValueError('bound must be min < max')),
    ('init_value_23',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.UNDEFINED,
         bound=(0, 100),
         cycle=10)),
        MXValueError('type cannot be undefined or void')),
    ('init_value_24',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.VOID,
         bound=(0, 100),
         cycle=10)),
        MXValueError('type cannot be undefined or void')),
    ('init_value_25',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=0)),
        MXValueError('cycle must be > 0')),
    ('init_value_26',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=-10)),
        MXValueError('cycle must be > 0')),
    ('init_value_27',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10,
         energy=100,
         desc='test description',
         thing_name='test_big_thing',
         middleware_name='test_middleware',
         format='txt')),
     b'\x80\x04\x95\x90\x01\x00\x00\x00\x00\x00\x00\x8c\x17big_thing_py.core.value\x94\x8c\x07MXValue\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x1efunc_no_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94Kd\x8c\x05_desc\x94\x8c\x10test description\x94\x8c\x0b_thing_name\x94\x8c\x0etest_big_thing\x94\x8c\x10_middleware_name\x94\x8c\x0ftest_middleware\x94\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kd\x8c\x06_cycle\x94K\n\x8c\x07_format\x94\x8c\x03txt\x94ub.'),
    ('init_value_28',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10,
         energy='100')),
        MXValueError('energy must be int or float')),
    ('init_value_29',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10,
         desc=100)),
        MXValueError('desc must be str')),
    ('init_value_30',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10,
         thing_name=100)),
        MXValueError('thing_name must be str')),
    ('init_value_31',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10,
         middleware_name=100)),
        MXValueError('middleware_name must be str')),
    ('init_value_32',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         type=MXType.INTEGER,
         bound=(0, 100),
         cycle=10,
         format=100)),
        MXValueError('format must be str')),
])
def test_init_value(test_id: str, input: Dict[str, dict], expected_output: Union[bytes, Exception]):

    def setup(input) -> str:
        args = input['args']
        return args

    def task(**args: dict):
        return MXValue(**args)

    args = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(**args)
    else:
        output = task(**args)
        assert pickle.dumps(output) == expected_output

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('init_function_0',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     b'\x80\x04\x95w\x02\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c func_with_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94(\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(h\x05\x8c\x04arg1\x94\x8c\x05_type\x94h \x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg2\x94h)h\x1d\x8c\x06double\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg3\x94h)h\x1d\x8c\x06string\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg4\x94h)h\x1d\x8c\x04bool\x94\x85\x94R\x94h*K\x00h+Kdube\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x1b\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ub.'),
    ('init_function_1',
     dict(args=dict(
         tag_list=[MXTag('tag1'), MXTag(
             'tag2'), MXTag('tag3')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     TypeError()),
    ('init_function_2',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     TypeError()),
    ('init_function_3',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))])),
     TypeError()),
    ('init_function_4',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     b'\x80\x04\x95w\x02\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c func_with_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94(\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(h\x05\x8c\x04arg1\x94\x8c\x05_type\x94h \x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg2\x94h)h\x1d\x8c\x06double\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg3\x94h)h\x1d\x8c\x06string\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg4\x94h)h\x1d\x8c\x04bool\x94\x85\x94R\x94h*K\x00h+Kdube\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x1b\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ub.'),
    ('init_function_5',
     dict(args=dict(
         func=func_with_argument_no_return,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.VOID)),
     b'\x80\x04\x95~\x02\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x1cfunc_with_argument_no_return\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x04void\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94(\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(h\x05\x8c\x04arg1\x94\x8c\x05_type\x94h\x1d\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg2\x94h)h\x1d\x8c\x06double\x94\x85\x94R\x94h-K\x00h.Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg3\x94h)h\x1d\x8c\x06string\x94\x85\x94R\x94h-K\x00h.Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg4\x94h)h\x1d\x8c\x04bool\x94\x85\x94R\x94h-K\x00h.Kdube\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x1b\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ub.'),
    ('init_function_6',
     dict(args=dict(
         func=None,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.VOID)),
     MXValueError('func must be callable')),
    ('init_function_7',
     dict(args=dict(
         func=10,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.VOID)),
     MXValueError('func must be callable')),
    ('init_function_8',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         tag_list=[],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     MXValueError('tag_list must contain MXTag object')),
    ('init_function_9',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     b'\x80\x04\x95R\x02\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c func_with_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sba\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x11\x8c\x10_middleware_name\x94h\x11\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94(\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(h\x05\x8c\x04arg1\x94\x8c\x05_type\x94h\x1a\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdubh\x1f)\x81\x94}\x94(h\x05\x8c\x04arg2\x94h#h\x17\x8c\x06double\x94\x85\x94R\x94h$K\x00h%Kdubh\x1f)\x81\x94}\x94(h\x05\x8c\x04arg3\x94h#h\x17\x8c\x06string\x94\x85\x94R\x94h$K\x00h%Kdubh\x1f)\x81\x94}\x94(h\x05\x8c\x04arg4\x94h#h\x17\x8c\x04bool\x94\x85\x94R\x94h$K\x00h%Kdube\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x15\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ub.'),
    ('init_function_10',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     b'\x80\x04\x95w\x02\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c func_with_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94(\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(h\x05\x8c\x04arg1\x94\x8c\x05_type\x94h \x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg2\x94h)h\x1d\x8c\x06double\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg3\x94h)h\x1d\x8c\x06string\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg4\x94h)h\x1d\x8c\x04bool\x94\x85\x94R\x94h*K\x00h+Kdube\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x1b\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ub.'),
    ('init_function_11',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     b'\x80\x04\x95w\x02\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c func_with_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94(\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(h\x05\x8c\x04arg1\x94\x8c\x05_type\x94h \x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg2\x94h)h\x1d\x8c\x06double\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg3\x94h)h\x1d\x8c\x06string\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg4\x94h)h\x1d\x8c\x04bool\x94\x85\x94R\x94h*K\x00h+Kdube\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x1b\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ub.'),
    ('init_function_12',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.UNDEFINED)),
     MXValueError('return_type cannot be undefined')),
    ('init_function_13',
     dict(args=dict(
         name='test_function1',
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     b'\x80\x04\x95e\x02\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x0etest_function1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94(\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(h\x05\x8c\x04arg1\x94\x8c\x05_type\x94h \x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg2\x94h)h\x1d\x8c\x06double\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg3\x94h)h\x1d\x8c\x06string\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg4\x94h)h\x1d\x8c\x04bool\x94\x85\x94R\x94h*K\x00h+Kdube\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x1b\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ub.'),
    ('init_function_14',
     dict(args=dict(
         name='test_function_1',
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     b'\x80\x04\x95f\x02\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x0ftest_function_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94(\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(h\x05\x8c\x04arg1\x94\x8c\x05_type\x94h \x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg2\x94h)h\x1d\x8c\x06double\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg3\x94h)h\x1d\x8c\x06string\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg4\x94h)h\x1d\x8c\x04bool\x94\x85\x94R\x94h*K\x00h+Kdube\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x1b\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ub.'),
    ('init_function_15',
     dict(args=dict(
         name='_test_function_1',
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     b'\x80\x04\x95g\x02\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x10_test_function_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94(\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(h\x05\x8c\x04arg1\x94\x8c\x05_type\x94h \x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg2\x94h)h\x1d\x8c\x06double\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg3\x94h)h\x1d\x8c\x06string\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg4\x94h)h\x1d\x8c\x04bool\x94\x85\x94R\x94h*K\x00h+Kdube\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x1b\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ub.'),
    ('init_function_16',
     dict(args=dict(
         name='1_test_function',
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_function_17',
     dict(args=dict(
         name='test-function',
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_function_18',
     dict(args=dict(
         name='test function',
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('init_function_19',
     dict(args=dict(
         name='',
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     b'\x80\x04\x95w\x02\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c func_with_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94(\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(h\x05\x8c\x04arg1\x94\x8c\x05_type\x94h \x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg2\x94h)h\x1d\x8c\x06double\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg3\x94h)h\x1d\x8c\x06string\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg4\x94h)h\x1d\x8c\x04bool\x94\x85\x94R\x94h*K\x00h+Kdube\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x1b\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ub.'),
    ('init_function_20',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER,
         energy='100')),
     MXValueError('energy must be int or float')),
    ('init_function_21',
     dict(args=dict(
         func=func_no_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[],
         return_type=MXType.INTEGER)),
     b'\x80\x04\x95\x98\x01\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x1efunc_no_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x1b\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ub.'),
    ('init_function_22',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                   MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)), MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     b'\x80\x04\x95w\x02\x00\x00\x00\x00\x00\x00\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c func_with_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag2\x94sbh\x0b)\x81\x94}\x94h\x05\x8c\x04tag3\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x17\x8c\x10_middleware_name\x94h\x17\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94(\x8c\x1abig_thing_py.core.argument\x94\x8c\nMXArgument\x94\x93\x94)\x81\x94}\x94(h\x05\x8c\x04arg1\x94\x8c\x05_type\x94h \x8c\x04_min\x94K\x00\x8c\x04_max\x94Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg2\x94h)h\x1d\x8c\x06double\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg3\x94h)h\x1d\x8c\x06string\x94\x85\x94R\x94h*K\x00h+Kdubh%)\x81\x94}\x94(h\x05\x8c\x04arg4\x94h)h\x1d\x8c\x04bool\x94\x85\x94R\x94h*K\x00h+Kdube\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x1b\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ub.'),
    ('init_function_23',
     dict(args=dict(
         func=func_with_argument_with_return_1,
         tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3'), MXTag('tag2')],
         arg_list=[MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)), MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100))],
         return_type=MXType.INTEGER)),
     MXValueError('Length of argument list must be same with callback function')),
])
def test_init_function(test_id: str, input: Dict[str, dict], expected_output: Union[MXFunction, Exception]):

    def setup(input) -> str:
        args = input['args']
        return args

    def task(**args: dict):
        return MXFunction(**args)

    args = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(**args)
    else:
        output = task(**args)
        assert pickle.dumps(output) == expected_output

####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('big_thing_init_0', dict(args=dict(name='test_big_thing1')),
     b'\x80\x04\x95\x17\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x0ftest_big_thing1\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_1', dict(args=dict(name='test_big_thing_1')),
     b'\x80\x04\x95\x18\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x10test_big_thing_1\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_2', dict(args=dict(name='_test_big_thing_1')),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11_test_big_thing_1\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_3', dict(args=dict(name='1_test_big_thing')),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('big_thing_init_4', dict(args=dict(name='test-big_thing')),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('big_thing_init_5', dict(args=dict(name='test big_thing')),
     MXValueError('name cannot be empty & can only contain alphanumeric characters and underscores')),
    ('big_thing_init_6', dict(args=dict(name='')),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_7', dict(args=dict()),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_8', dict(args=dict()),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_9', dict(args=dict(alive_cycle=120)),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94Kx\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_10', dict(args=dict(alive_cycle=0)),
     MXValueError('alive cycle must be greater than 0')),
    ('big_thing_init_11', dict(args=dict(alive_cycle=-120)),
     MXValueError('alive cycle must be greater than 0')),
    ('big_thing_init_12', dict(args=dict()),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_13', dict(args=dict(is_super=True, is_parallel=True)),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x88\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_14', dict(args=dict(is_super=False, is_parallel=True)),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_15', dict(args=dict(is_super=False, is_parallel=False)),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x89\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_16', dict(args=dict(is_super=True, is_parallel=False)),
     MXValueError('Super Thing must be parallel')),
    ('big_thing_init_17', dict(args=dict()),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_18', dict(args=dict(ip='127.0.0.1')),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_19', dict(args=dict(ip='localhost')),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_20', dict(args=dict(ip='123.123.123.123.123')),
     Exception()),
    ('big_thing_init_21', dict(args=dict(ip='123.123.123')),
     Exception()),
    ('big_thing_init_22', dict(args=dict(ip='1234.123.123.123')),
     Exception()),
    ('big_thing_init_23', dict(args=dict(ip='123.123.123.-1')),
     Exception()),
    ('big_thing_init_24', dict(args=dict(ip='')),
     b'\x80\x04\x95\x17\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\x070.0.0.0\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_25', dict(args=dict(ip='not.exist.url')),
     Exception()),
    ('big_thing_init_26', dict(args=dict()),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_27', dict(args=dict(port=1883)),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_28', dict(args=dict(port=0)),
     MXValueError('Invalid IP address, port number')),
    ('big_thing_init_29', dict(args=dict(port=-100)),
     MXValueError('Invalid IP address, port number')),
    ('big_thing_init_30', dict(args=dict(port=65535)),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M\xff\xff\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_31', dict(args=dict(port=65536)),
     MXValueError('Invalid IP address, port number')),
    ('big_thing_init_32', dict(args=dict()),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_33', dict(args=dict(ssl_enable=False)),
     b'\x80\x04\x95\x19\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x00\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_34', dict(args=dict(ssl_enable=False, ssl_ca_path='/path/to/ssl/config')),
     b'\x80\x04\x95,\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c\x13/path/to/ssl/config\x94\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_35', dict(args=dict(ssl_enable=True)),
     MXValueError('ssl_enable is True but ssl_ca_path is empty')),
    ('big_thing_init_36', dict(args=dict(ssl_enable=True, ssl_ca_path='/path/to/ssl/config')),
     MXValueError('SSL CA file not found')),
    ('big_thing_init_37', dict(args=dict(ssl_enable=True, ssl_ca_path=f'{get_project_root()}/res/CA')),
     b'\x80\x04\x95C\x01\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88\x8c\x10_middleware_name\x94N\x8c\x0e_function_list\x94]\x94\x8c\x0b_value_list\x94]\x94\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94\x8c*/home/thsvkd/Workspace/big-thing-py/res/CA\x94\x8c\x0b_ssl_enable\x94\x88\x8c\x13_append_mac_address\x94\x88ub.'),
    ('big_thing_init_38', dict(args=dict(service_list=[MXValue(func=func_no_argument_with_return_1, tag_list=[MXTag('tag1')], type=MXType.INTEGER, bound=(0, 100), cycle=10),
                                                       MXFunction(func=func_no_argument_with_return_1, tag_list=[MXTag('tag1')], return_type=MXType.INTEGER)])),
     b'\x80\x04\x95\x92\x03\x00\x00\x00\x00\x00\x00\x8c\x16big_thing_py.big_thing\x94\x8c\nMXBigThing\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x11default_big_thing\x94\x8c\r_service_list\x94]\x94(\x8c\x17big_thing_py.core.value\x94\x8c\x07MXValue\x94\x93\x94)\x81\x94}\x94(h\x05\x8c\x1efunc_no_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x05h\x06sbh\x13)\x81\x94}\x94h\x05\x8c\x04tag1\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x06\x8c\x10_middleware_name\x94h\x1b\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kd\x8c\x06_cycle\x94K\n\x8c\x07_format\x94h\x1bub\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(h\x05h\x0eh\x0f]\x94(h\x13)\x81\x94}\x94h\x05h\x06sbh\x13)\x81\x94}\x94h\x05h\x18sbeh\x19K\x00h\x1ah\x1bh\x1ch\x06h\x1dh\x1b\x8c\x0c_return_type\x94h$\x8c\t_arg_list\x94]\x94\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x1f\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ube\x8c\x0c_alive_cycle\x94K<\x8c\t_is_super\x94\x89\x8c\x0c_is_parallel\x94\x88h\x1dN\x8c\x0e_function_list\x94]\x94(h+)\x81\x94}\x94(h\x05\x8c __func_no_argument_with_return_1\x94h\x0f]\x94(h\x13)\x81\x94}\x94h\x05h\x06sbh\x13)\x81\x94}\x94h\x05h\x18sbeh\x19K\x00h\x1ah\x1bh\x1ch\x06h\x1dh\x1bh3h$h4]\x94h6K\x00h7K\x00h8h=ubh,e\x8c\x0b_value_list\x94]\x94h\x0ca\x8c\x03_ip\x94\x8c\t127.0.0.1\x94\x8c\x05_port\x94M[\x07\x8c\x0c_ssl_ca_path\x94h\x1b\x8c\x0b_ssl_enable\x94\x89\x8c\x13_append_mac_address\x94\x88ub.'),
])
def test_init_big_thing(test_id: str, input: Dict[str, dict], expected_output: Union[MXBigThing, MXService, Exception]):

    def setup(input) -> str:
        args = input['args']
        return args

    def task(**args: dict) -> MXBigThing:
        return MXBigThing(**args)

    args = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(**args)
    else:
        output = task(**args)
        assert pickle.dumps(output) == expected_output


# ####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('value_add_0', dict(value=MXValue(func=func_no_argument_with_return_1, tag_list=[MXTag('tag1')], type=MXType.INTEGER, bound=(0, 100), cycle=10)),
     b'\x80\x04\x95M\x02\x00\x00\x00\x00\x00\x00]\x94(\x8c\x17big_thing_py.core.value\x94\x8c\x07MXValue\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x1efunc_no_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x06\x8c\x11default_big_thing\x94sbh\x0c)\x81\x94}\x94h\x06\x8c\x04tag1\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x0f\x8c\x10_middleware_name\x94h\x15\x8c\x05_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\x04_min\x94K\x00\x8c\x04_max\x94Kd\x8c\x06_cycle\x94K\n\x8c\x07_format\x94h\x15ub\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(h\x06\x8c __func_no_argument_with_return_1\x94h\x08]\x94(h\x0c)\x81\x94}\x94h\x06h\x0fsbh\x0c)\x81\x94}\x94h\x06h\x12sbeh\x13K\x00h\x14h\x15h\x16h\x0fh\x17h\x15\x8c\x0c_return_type\x94h\x1e\x8c\t_arg_list\x94]\x94\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x19\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94ube.')
])
def test_add_value_service(test_id: str, input: Dict[str, dict], expected_output: List[MXService], big_thing: MXBigThing):

    def setup(input, big_thing: MXBigThing) -> MXBigThing:
        value = input['value']
        big_thing.add_service(value)
        return big_thing

    def task(big_thing: MXBigThing) -> List[MXService]:
        result = big_thing.get_value_list() + big_thing.get_function_list()
        return result

    big_thing = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing)
    else:
        output = task(big_thing)
        assert pickle.dumps(output) == expected_output

# ####################################################################################################################################


function_add_1_test_expected_output_function = MXFunction(func=func_no_argument_with_return_1, tag_list=[MXTag(
    MXBigThing.DEFAULT_NAME), MXTag('tag1')], return_type=MXType.INTEGER, thing_name=MXBigThing.DEFAULT_NAME)


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('function_add_0', dict(function=MXFunction(func=func_no_argument_with_return_1, tag_list=[MXTag('tag1')], return_type=MXType.INTEGER, thing_name=MXBigThing.DEFAULT_NAME)),
     b'\x80\x04\x95\x96\x01\x00\x00\x00\x00\x00\x00]\x94\x8c\x1abig_thing_py.core.function\x94\x8c\nMXFunction\x94\x93\x94)\x81\x94}\x94(\x8c\x05_name\x94\x8c\x1efunc_no_argument_with_return_1\x94\x8c\t_tag_list\x94]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94h\x06\x8c\x11default_big_thing\x94sbh\x0c)\x81\x94}\x94h\x06\x8c\x04tag1\x94sbe\x8c\x07_energy\x94K\x00\x8c\x05_desc\x94\x8c\x00\x94\x8c\x0b_thing_name\x94h\x0f\x8c\x10_middleware_name\x94h\x15\x8c\x0c_return_type\x94\x8c\x1abig_thing_py.common.mxtype\x94\x8c\x06MXType\x94\x93\x94\x8c\x03int\x94\x85\x94R\x94\x8c\t_arg_list\x94]\x94\x8c\n_exec_time\x94K\x00\x8c\x08_timeout\x94K\x00\x8c\x0b_range_type\x94h\x19\x8c\x0bMXRangeType\x94\x93\x94\x8c\x06single\x94\x85\x94R\x94uba.')
])
def test_add_function_service(test_id: str, input: dict, expected_output: List[MXFunction], big_thing: MXBigThing):

    def setup(input, big_thing: MXBigThing) -> MXBigThing:
        function = input['function']
        big_thing.add_service(function)
        return big_thing

    def task(big_thing: MXBigThing) -> List[MXService]:
        result = big_thing.get_function_list()
        return result

    big_thing = setup(input, big_thing)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(big_thing)
    else:
        output = task(big_thing)
        assert pickle.dumps(output) == expected_output

# ####################################################################################################################################


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('tag_add_0', dict(service=MXValue(func=func_no_argument_with_return_1, tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')], type=MXType.INTEGER, bound=(0, 100), cycle=10), tag_list=[MXTag('tag4'), MXTag('tag5')]),
     b'\x80\x04\x95\x85\x00\x00\x00\x00\x00\x00\x00]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94\x8c\x05_name\x94\x8c\x04tag1\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag2\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag3\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag4\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag5\x94sbe.'),
    ('tag_add_1', dict(service=MXFunction(func=func_no_argument_with_return_1, tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')], return_type=MXType.INTEGER), tag_list=[MXTag('tag4'), MXTag('tag5')]),
     b'\x80\x04\x95\x85\x00\x00\x00\x00\x00\x00\x00]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94\x8c\x05_name\x94\x8c\x04tag1\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag2\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag3\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag4\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag5\x94sbe.'),
    ('tag_add_2', dict(service=MXValue(func=func_no_argument_with_return_1, tag_list=[MXTag('tag1'), MXTag('tag2'), MXTag('tag3')], type=MXType.INTEGER, bound=(0, 100), cycle=10), tag_list=[MXTag('tag4'), MXTag('tag5')] + [MXTag('tag5'), MXTag('tag6')]),
     b'\x80\x04\x95\x97\x00\x00\x00\x00\x00\x00\x00]\x94(\x8c\x15big_thing_py.core.tag\x94\x8c\x05MXTag\x94\x93\x94)\x81\x94}\x94\x8c\x05_name\x94\x8c\x04tag1\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag2\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag3\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag4\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag5\x94sbh\x03)\x81\x94}\x94h\x06\x8c\x04tag6\x94sbe.'),
])
def test_add_tag(test_id, input: Dict[str, Union[MXService, List[MXTag]]], expected_output: List[MXTag]):

    def setup(input) -> MXService:
        service: MXService = input['service']
        tag_list = input['tag_list']
        service.add_tag(tag_list)
        return service

    def task(service: MXService) -> List[MXTag]:
        result = service.get_tag_list()
        return result

    service = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task(service)
    else:
        output = task(service)
        assert pickle.dumps(output) == expected_output


####################################################################################################################################


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
