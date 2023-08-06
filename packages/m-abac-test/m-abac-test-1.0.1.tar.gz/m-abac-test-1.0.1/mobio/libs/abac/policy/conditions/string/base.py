"""
    String conditions base class
"""

import logging

from marshmallow import Schema, fields, EXCLUDE, validate

from ..base import ConditionBase, ABCMeta, abstractmethod

LOG = logging.getLogger(__name__)


def is_string(value) -> bool:
    """
        Check if value is string
    """
    return isinstance(value, str)


class StringCondition(ConditionBase, metaclass=ABCMeta):
    """
        Base class for string conditions
    """

    def __init__(self, values, what, qualifier=ConditionBase.Qualifier.ForAnyValue, ignore_case=False, **kwargs):
        self.case_insensitive = ignore_case
        self.values = values
        self.what = what
        self.qualifier = qualifier


    @abstractmethod
    def _is_satisfied(self) -> bool:
        """
            Is string conditions satisfied

            :param what: string value to check
            :return: True if satisfied else False
        """
        raise NotImplementedError()


class StringConditionSchema(Schema):
    """
        Base JSON schema for string conditions
    """
    values = fields.List(fields.String(required=True, allow_none=False), required=True, allow_none=False)
    ignore_case = fields.Bool(default=False, missing=False)
    what = fields.String(required=True, allow_none=False)
    qualifier = fields.String(allow_none=False, load_default=ConditionBase.Qualifier.ForAnyValue,
                            validate=validate.OneOf(ConditionBase.Qualifier.ALL))

    class Meta:
        unknown = EXCLUDE