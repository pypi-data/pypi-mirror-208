from big_thing_py.core.thing import *
import functools


class MXStaffThing(MXThing, metaclass=ABCMeta):
    def __init__(self, name: str, service_list: List[MXService], alive_cycle: float, is_super: bool = False, is_parallel: bool = True,
                 device_id: str = None):
        super().__init__(name, service_list, alive_cycle, is_super, is_parallel)
        self._device_id = device_id
        self._is_connected = False

        self._receive_queue: Queue = Queue()
        self._publish_queue: Queue = Queue()

    # TODO: Check this method works correct
    def __eq__(self, o: 'MXStaffThing') -> bool:
        instance_check = isinstance(o, MXStaffThing)
        device_id_check = (o._device_id == self._device_id)

        return super().__eq__(o) and instance_check and device_id_check

    def get_device_id(self) -> str:
        return self._device_id

    def set_device_id(self, id: str) -> None:
        self._device_id = id

    def is_connected(self) -> bool:
        return self._is_connected

    def set_function_result_queue(self, queue: Queue) -> None:
        for function in self._function_list:
            function.set_publish_queue(queue)

    def print_func_info(func: Callable):

        @functools.wraps(func)
        def wrap(self: MXStaffThing, *args, **kwargs):
            MXLOG_DEBUG(
                f'{func.__name__} at {self._name} actuate!!!', 'green')
            ret = func(self, *args, **kwargs)
            return ret
        # TODO: 함수가 데코레이팅 되었으면 staff thing의 service list에 추가하는 기능을 구현하고자 추가함
        # TODO: 근데 위에 @functools.wraps(func)기능과 동시에 사용이 가능한지 확인해야함
        wrap.is_decorated = True
        return wrap

    @abstractmethod
    def make_service_list(self):
        pass
