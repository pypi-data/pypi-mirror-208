from big_thing_py.utils import *


class SoPArgument:

    def __init__(self, name: str = None, type: SoPType = None, bound: Tuple[float, float] = (None, None)):
        self._name: str = name
        self._type: SoPType = type
        self._min: float = bound[0]
        self._max: float = bound[1]

    def __str__(self) -> str:
        return self._name

    def __eq__(self, o: 'SoPArgument') -> bool:
        instance_check = isinstance(o, SoPArgument)
        name_check = (o._name == self._name)
        type_check = (o._type == self._type)
        min_check = (o._min == self._min)
        max_check = (o._max == self._max)

        return instance_check and name_check and type_check and min_check and max_check

    def dump(self) -> Dict:
        return {
            "type": self._type.value,
            "name": self._name,
            "bound": {
                "min_value": self._min,
                "max_value": self._max
            }
        }
