from marshmallow import post_load
from .base import DayCondition, DayConditionSchema


class DayLt(DayCondition):

    def _is_satisfied(self) -> bool:
        if not self.check_format_input_day(self.what):
            return False
        if self.qualifier == self.Qualifier.ForAnyValue:
            for i in self.values:
                if self.check_format_input_day(i):
                    if self.what < i:
                        return True
            return False
        else:
            for i in self.values:
                if not self.check_format_input_day(i):
                    return False
                if self.what >= i:
                    return False
            return True


class DayLtSchema(DayConditionSchema):
    """
        JSON schema for greater than datetime condition
    """

    @post_load
    def post_load(self, data, **_):  # pylint: disable=missing-docstring,no-self-use
        # self.validate(data)
        return DayLt(**data)
