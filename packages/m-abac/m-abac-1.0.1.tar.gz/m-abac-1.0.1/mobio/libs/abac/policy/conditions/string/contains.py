"""
    String contains conditions
"""

from marshmallow import post_load

from .base import StringCondition, StringConditionSchema


class Contains(StringCondition):
    """
        Condition for string `self.what` contains `value`
    """

    def _is_satisfied(self) -> bool:
        if self.qualifier == self.Qualifier.ForAnyValue:
            for i in self.values:
                if self.case_insensitive:
                    if self.what.lower() in i.lower():
                        return True
                else:
                    if self.what in i:
                        return True
            return False
        else:
            for i in self.values:
                if self.case_insensitive:
                    if self.what.lower() not in i.lower():
                        return False
                else:
                    if self.what not in i:
                        return False
            return True

class ContainsSchema(StringConditionSchema):
    """
        JSON schema for contains string conditions
    """

    @post_load
    def post_load(self, data, **_):  # pylint: disable=missing-docstring,no-self-use
        # self.validate(data)
        return Contains(**data)
