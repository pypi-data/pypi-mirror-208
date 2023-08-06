from big_thing_py.tests.thing_factory import *
from big_thing_py.tests.conftest import PARAMETRIZE_STRING
import pytest


@pytest.mark.parametrize(PARAMETRIZE_STRING, [
    ('gen_thing_id_0', dict(big_thing=MXBigThing(append_mac_address=True), interface=None),
     f'{MXBigThing.DEFAULT_NAME}_{get_mac_address()}'),
    ('gen_thing_id_1', dict(big_thing=MXBigThing(append_mac_address=True), interface='not_vaild_device'),
     Exception()),
    ('gen_thing_id_2', dict(big_thing=MXBigThing(append_mac_address=False), interface=None),
     MXBigThing.DEFAULT_NAME),
])
def test_generate_thing_id(test_id: str, input: Dict[str, Union[MXBigThing, str]], expected_output: str):

    def setup(input) -> Tuple[MXBigThing, str]:
        big_thing = input['big_thing']
        interface = input['interface']

        return big_thing, interface

    def task1(big_thing: MXBigThing, interface: str) -> str:
        result = big_thing._generate_thing_id(**dict(name=big_thing.get_name(), interface=interface))

        return result

    def task2(big_thing: MXBigThing, interface: str) -> str:
        output = big_thing._generate_thing_id(**dict(name=big_thing.get_name(), interface=interface))

        assert MXBigThing.DEFAULT_NAME in output and len(output) - len(MXBigThing.DEFAULT_NAME) == 13
        raise

    big_thing, interface = setup(input)
    if isinstance(expected_output, Exception):
        with pytest.raises(type(expected_output), match=str(expected_output)):
            task2(big_thing, interface)
    else:
        output = task1(big_thing, interface)
        assert output == expected_output

####################################################################################################################################


if __name__ == '__main__':
    pytest.main(['-s', '-vv', __file__])
