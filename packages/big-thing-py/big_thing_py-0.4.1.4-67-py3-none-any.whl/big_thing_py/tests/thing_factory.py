from big_thing_py.super_thing import *


@static_vars(count=0)
def func_no_argument_with_increase_int() -> int:
    func_no_argument_with_increase_int.count += 1
    return func_no_argument_with_increase_int.count


@static_vars(count=0)
def func_with_argument_with_increase_int(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> int:
    func_with_argument_with_increase_int.count += 1
    return func_with_argument_with_increase_int.count


def func_with_timeout_argument_with_return_1(timeout: float) -> str:
    time.sleep(timeout)
    return 1


def func_no_argument_with_return_binary() -> str:
    return file_to_base64(__file__)


def func_with_argument_with_return_binary(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> str:
    return file_to_base64(__file__)


def func_no_argument_no_return() -> None:
    pass


def func_no_argument_no_return() -> None:
    pass


def func_no_argument_no_return() -> None:
    pass


def func_no_argument_with_return_1() -> int:
    return 1


def func_no_argument_with_return_2() -> int:
    return 2


def func_no_argument_with_return_3() -> int:
    return 3


def func_with_argument_no_return(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> None:
    pass


def func_with_argument_no_return(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> None:
    pass


def func_with_argument_no_return(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> None:
    pass


def func_with_argument_with_return_1(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> int:
    return 1


def func_with_argument_with_return_2(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> int:
    return 2


def func_with_argument_with_return_3(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> int:
    return 3


class BigThingFactory:

    @staticmethod
    @static_vars(count=0)
    def func_no_argument_with_increase_int() -> int:
        BigThingFactory.func_no_argument_with_increase_int.count += 1
        return BigThingFactory.func_no_argument_with_increase_int.count

    @staticmethod
    @static_vars(count=0)
    def func_with_argument_with_increase_int(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> int:
        BigThingFactory.func_with_argument_with_increase_int.count += 1
        return BigThingFactory.func_with_argument_with_increase_int.count

    @staticmethod
    def func_with_timeout_argument_with_return1(timeout: float) -> str:
        time.sleep(timeout)
        return 1

    @staticmethod
    def func_no_argument_with_return_binary() -> str:
        return file_to_base64(__file__)

    @staticmethod
    def func_with_argument_with_return_binary(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> str:
        return file_to_base64(__file__)

    @staticmethod
    def func_no_argument_no_return1() -> None:
        pass

    @staticmethod
    def func_no_argument_no_return2() -> None:
        pass

    @staticmethod
    def func_no_argument_no_return3() -> None:
        pass

    @staticmethod
    def func_no_argument_with_return1() -> int:
        return 1

    @staticmethod
    def func_no_argument_with_return2() -> int:
        return 2

    @staticmethod
    def func_no_argument_with_return3() -> int:
        return 3

    @staticmethod
    def func_with_argument_no_return1(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> None:
        pass

    @staticmethod
    def func_with_argument_no_return2(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> None:
        pass

    @staticmethod
    def func_with_argument_no_return3(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> None:
        pass

    @staticmethod
    def func_with_argument_with_return1(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> int:
        return 1

    @staticmethod
    def func_with_argument_with_return2(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> int:
        return 2

    @staticmethod
    def func_with_argument_with_return3(int_arg: int, float_arg: float, str_arg: str, bool_arg: bool) -> int:
        return 3

    ########################################################

    def __init__(self) -> None:
        pass

    def create_tags(self) -> List[MXTag]:
        return [MXTag('tag1'), MXTag('tag2'), MXTag('tag3')]

    def create_values(self) -> List[MXValue]:
        tag_list = self.create_tags()
        return [MXValue(name='value1', func=BigThingFactory.func_no_argument_with_return1, tag_list=tag_list, type=MXType.INTEGER, bound=(0, 100), cycle=10),
                MXValue(name='value2', func=BigThingFactory.func_no_argument_with_return2, tag_list=tag_list, type=MXType.INTEGER, bound=(0, 100), cycle=10),]

    def create_binary_value(self) -> MXValue:
        tag_list = self.create_tags()
        return MXValue(name='binary_value1', func=BigThingFactory.func_no_argument_with_return_binary, tag_list=tag_list, type=MXType.BINARY, bound=(0, 1024 * 1000), cycle=60)

    def create_functions(self) -> List[MXFunction]:
        tag_list = self.create_tags()
        return [MXFunction(name='function1', func=BigThingFactory.func_no_argument_no_return1, tag_list=tag_list, arg_list=[], return_type=MXType.INTEGER, exec_time=1, energy=100),
                MXFunction(name='function2', func=BigThingFactory.func_no_argument_no_return2, tag_list=tag_list, arg_list=[], return_type=MXType.INTEGER, exec_time=1, energy=100)]

    def create_functions_return(self) -> List[MXFunction]:
        tag_list = self.create_tags()
        return [MXFunction(name='function1', func=BigThingFactory.func_no_argument_with_return1, tag_list=tag_list, arg_list=[], return_type=MXType.INTEGER, exec_time=1, energy=100),
                MXFunction(name='function2', func=BigThingFactory.func_no_argument_with_return2, tag_list=tag_list, arg_list=[], return_type=MXType.INTEGER, exec_time=1, energy=100)]

    def create_functions_arg(self) -> List[MXFunction]:
        tag_list = self.create_tags()
        arg_list = self.create_arguments()
        return [MXFunction(name='function1', func=BigThingFactory.func_with_argument_no_return1, tag_list=tag_list, arg_list=arg_list, return_type=MXType.INTEGER, exec_time=1, energy=100),
                MXFunction(name='function2', func=BigThingFactory.func_with_argument_no_return2, tag_list=tag_list, arg_list=arg_list, return_type=MXType.INTEGER, exec_time=1, energy=100)]

    def create_functions_arg_return(self) -> List[MXFunction]:
        tag_list = self.create_tags()
        arg_list = self.create_arguments()
        return [MXFunction(name='function1', func=BigThingFactory.func_with_argument_with_return1, tag_list=tag_list, arg_list=arg_list, return_type=MXType.INTEGER, exec_time=1, energy=100),
                MXFunction(name='function2', func=BigThingFactory.func_with_argument_with_return2, tag_list=tag_list, arg_list=arg_list, return_type=MXType.INTEGER, exec_time=1, energy=100)]

    def create_timeout_function(self, timeout: float = 1) -> MXFunction:
        tag_list = self.create_tags()
        arg_list = [MXArgument(name='timeout', type=MXType.DOUBLE, bound=(0, 1000000))]
        return MXFunction(name='timeout_function1', func=BigThingFactory.func_with_timeout_argument_with_return1, tag_list=tag_list, arg_list=arg_list, return_type=MXType.INTEGER, exec_time=1, timeout=timeout, energy=100)

    def create_arguments(self) -> List[MXArgument]:
        return [MXArgument(name='arg1', type=MXType.INTEGER, bound=(0, 100)),
                MXArgument(name='arg2', type=MXType.DOUBLE, bound=(0, 100)),
                MXArgument(name='arg3', type=MXType.STRING, bound=(0, 100)),
                MXArgument(name='arg4', type=MXType.BOOL, bound=(0, 100))]

    def create_default_thing(self) -> MXBigThing:
        value_list = self.create_values()
        function_list = self.create_functions_arg_return()
        thing = MXBigThing(service_list=value_list + function_list)
        return thing

    def create_type_A_thing(self) -> MXBigThing:
        value_list = self.create_values()
        function_list = self.create_functions_arg_return()
        thing = MXBigThing(name='test_thing', service_list=value_list + function_list)
        return thing

    def create_type_B_thing(self) -> MXBigThing:
        value_list = self.create_values()
        function_list = self.create_functions_arg_return()
        thing = MXBigThing(name='',
                           service_list=value_list + function_list)
        return thing

    def create_type_C_thing(self) -> MXBigThing:
        thing = MXBigThing(name='test_thing',
                           service_list=[])
        return thing

    def create_type_D_thing(self) -> MXBigThing:
        value_list = self.create_values()
        function_list = self.create_functions_arg_return()
        thing = MXBigThing(name='test_thing',
                           service_list=value_list + function_list,
                           is_super=True,)
        return thing

    def create_type_E_thing(self) -> MXBigThing:
        value_list = self.create_values()
        function_list = self.create_functions_arg_return()
        for service in value_list + function_list:
            service.set_tag_list([])
        thing = MXBigThing(name='test_thing',
                           service_list=value_list + function_list)
        return thing

    def create_type_F_thing(self) -> MXBigThing:
        value_list = self.create_values()
        function_list = self.create_functions_arg_return()
        for service in value_list + function_list:
            service.set_name('')
        thing = MXBigThing(name='test_thing',
                           service_list=value_list + function_list)
        return thing

    def create_type_G_thing(self) -> MXBigThing:
        value_list = self.create_values()
        function_list = self.create_functions_arg_return()
        for value in value_list:
            value.set_format('something')
        thing = MXBigThing(name='test_thing',
                           service_list=value_list + function_list)
        return thing

    def create_type_H_thing(self) -> MXBigThing:
        value_list = self.create_values()
        function_list = self.create_functions_arg_return()
        for function in function_list:
            function.set_exec_time(-10)
            function.set_energy(-10)
        thing = MXBigThing(name='test_thing',
                           service_list=value_list + function_list)
        return thing

    def create_type_I_thing(self) -> MXBigThing:
        value_list = self.create_values()
        function_list = self.create_functions_arg_return()
        for function in function_list:
            for arg in function.get_arg_list():
                arg.set_name('')
        thing = MXBigThing(name='test_thing',
                           service_list=value_list + function_list)
        return thing

    def create_type_J_thing(self) -> MXBigThing:
        value_list = self.create_values()
        function_list = self.create_functions_arg_return()
        for value in value_list:
            value.set_bound((0, -1))
        for function in function_list:
            for arg in function.get_arg_list():
                arg.set_bound((0, -1))
        thing = MXBigThing(name='test_thing',
                           service_list=value_list + function_list)
        return thing
