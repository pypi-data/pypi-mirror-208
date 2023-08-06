"""
    Operation base class
"""

from abc import ABCMeta, abstractmethod

# from py_abac.context import EvaluationContext

MapAnyValue = ""

class ConditionBase(metaclass=ABCMeta):
    """
        Base class for conditions
    """

    # @abstractmethod
    # def is_satisfied(self, ctx: EvaluationContext) -> bool:
    #     """
    #         Is conditions satisfied?
    #
    #         :param ctx: evaluation context
    #         :return: True if satisfied else False
    #     """
    #     raise NotImplementedError()

    class Qualifier:
        ForAnyValue = "ForAnyValue"
        ForAllValues = "ForAllValues"
        ALL = [ForAnyValue, ForAllValues]