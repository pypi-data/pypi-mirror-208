"""
    String not contains conditions
"""

from marshmallow import post_load

from .base import StringCondition, StringConditionSchema


class NotContains(StringCondition):
    """
        Condition for string `self.what` not contains `value`
    """

    def _is_satisfied(self) -> bool:
        if self.qualifier == self.Qualifier.ForAnyValue:
            for i in self.values:
                if self.case_insensitive:
                    if self.what.lower() in i.lower():
                        return False
                else:
                    if self.what in i:
                        return False
            return True
        else:
            for i in self.values:
                if self.case_insensitive:
                    if self.what.lower() in i.lower():
                        return False
                else:
                    if self.what in i:
                        return False
            return True


class NotContainsSchema(StringConditionSchema):
    """
        JSON schema for not contains string condition
    """

    @post_load
    def post_load(self, data, **_):  # pylint: disable=missing-docstring,no-self-use
        # self.validate(data)
        return NotContains(**data)
