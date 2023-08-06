"""
    String not equals conditions
"""

from marshmallow import post_load

from .base import StringCondition, StringConditionSchema


class NotEquals(StringCondition):
    """
        Condition for string `self.what` not equals `value`
    """

    def _is_satisfied(self) -> bool:
        if self.qualifier == self.Qualifier.ForAnyValue:
            for i in self.values:
                if self.case_insensitive:
                    if self.what.lower() != i.lower():
                        return True
                else:
                    if self.what != i:
                        return True
            return False
        else:
            for i in self.values:
                if self.case_insensitive:
                    if self.what.lower() == i.lower():
                        return False
                else:
                    if self.what == i:
                        return False
            return True


class NotEqualsSchema(StringConditionSchema):
    """
        JSON schema for not equals string condition
    """

    @post_load
    def post_load(self, data, **_):  # pylint: disable=missing-docstring,no-self-use
        # self.validate(data)
        return NotEquals(**data)
