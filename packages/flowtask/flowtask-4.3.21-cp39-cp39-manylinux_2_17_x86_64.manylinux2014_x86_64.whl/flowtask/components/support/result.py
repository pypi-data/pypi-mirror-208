from abc import ABC
from typing import Optional, Any
from collections.abc import Iterable


class ResultSupport(ABC):
    """Support for manipulating the results of Components.
    """
    def __init__(self, **kwargs):
        # collection of results:
        self._result: Optional[Any] = None
        self.data: Optional[Any] = None
        # previous Component
        self._component: Optional[Iterable] = None
        # can pass a previous data as Argument:
        try:
            self._input_result = kwargs['input_result']
            del kwargs['input_result']
        except KeyError:
            self._input_result = None

    def output(self):
        return self._result

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value

    @property
    def input(self):
        if isinstance(self._component, list):
            # TODO: get an array the results from different components
            result = []
            for component in self._component:
                if component:
                    result.append(component.output())
            if len(result) == 1:
                return result[0]
            else:
                return result
        elif self._component:
            return self._component.output()
        else:
            return self._input_result

    @property
    def previous(self):
        if self._component is not None:
            return self._component
        elif self._input_result is not None:
            return self ## result data is already on component
        else:
            return None
