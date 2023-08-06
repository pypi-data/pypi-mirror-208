"""
    String conditions base class
"""

import logging
import datetime
from marshmallow import Schema, fields, EXCLUDE, validate

from ..base import ConditionBase, ABCMeta, abstractmethod

LOG = logging.getLogger(__name__)


class DayCondition(ConditionBase, metaclass=ABCMeta):
    """
        Base class for string conditions
    """

    class DateFormat:
        ISO_FORMAT = "%Y-%m-%d"

    def __init__(self, values, what, date_format=DateFormat.ISO_FORMAT, qualifier=ConditionBase.Qualifier.ForAnyValue, **kwargs):
        self.values = values
        self.what = what
        self.qualifier = qualifier
        self.date_format = date_format


    @abstractmethod
    def _is_satisfied(self) -> bool:
        """
            Is string conditions satisfied

            :param what: string value to check
            :return: True if satisfied else False
        """
        raise NotImplementedError()

    def convert_str_to_date(self, d_str):
        try:
            return datetime.datetime.strptime(d_str, self.DateFormat.ISO_FORMAT)
        except:
            return None

    def check_format_input_day(self, i):
        if isinstance(i, str):
            if self.convert_str_to_date(i):
                return True
        return False


class DayConditionSchema(Schema):
    """
        Base JSON schema for string conditions
    """
    values = fields.List(fields.Raw(required=True, allow_none=False), required=True, allow_none=False)
    what = fields.String(required=True, allow_none=False)
    qualifier = fields.String(allow_none=False, load_default=ConditionBase.Qualifier.ForAnyValue,
                            validate=validate.OneOf([ConditionBase.Qualifier.ALL]))
    date_format = fields.String(allow_none=False, load_default=DayCondition.DateFormat.ISO_FORMAT,)

    class Meta:
        unknown = EXCLUDE