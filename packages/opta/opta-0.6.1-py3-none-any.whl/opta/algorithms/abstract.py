import json
from abc import ABC, abstractmethod

from opta.tools.coding import DecodeToNumpy, EncodeFromNumpy


class TerminationException(Exception):
    """Exception that is used to terminate algorithm"""

    pass


class OptimizationAlgorithm(ABC):
    """Class that should be inherited by optimization algorithms"""

    @abstractmethod
    def initialize(self, f, search_area):
        """Initialization procedure based on target function `f` and `search_area`"""
        raise NotImplementedError()

    @abstractmethod
    def iterate(self, f, search_area):
        """Iteration procedure based on target function `f` and `search_area`"""
        raise NotImplementedError()

    @abstractmethod
    def terminate(self, f, search_area):
        """Iteration procedure based on target function `f` and `search_area`"""
        raise NotImplementedError()

    def serialize(self):
        """Serialization procedure"""
        return json.dumps(self.__dict__, indent=4, cls=EncodeFromNumpy)

    def deserialize(self, state):
        """Deserialization procedure"""
        self.__dict__ = json.loads(state, cls=DecodeToNumpy)

    def optimize(self, f, search_area, number_of_iterations, **kwargs):
        """Optimization cycle of target function `f` on `search_area`
        that consists of initialization, followed by repeating cycle of
        iteration procedures (until termination criterion is fullfilled),
        and termination"""
        if not kwargs.get("skip_init", False):
            self.initialize(f, search_area)
        for _ in range(number_of_iterations):
            try:
                self.iterate(f, search_area)
            except TerminationException:
                break
        solution = self.terminate(f, search_area)
        return solution
