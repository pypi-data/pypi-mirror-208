"""
    Condition one-of schema
"""
from marshmallow import EXCLUDE
from marshmallow_oneofschema import OneOfSchema
from .boolean import *
from .collection import *
from .date_time import *
from .ip_address import *
from .numeric import *
from .string import *
from .day import *
from .others import *

class ConditionSchema(OneOfSchema):
    """
        Polymorphic JSON schema for conditions
    """
    type_field = "operator"
    type_schemas = {
        "StringEquals": EqualsSchema,
        "StringNotEquals": NotEqualsSchema,
        "StringContains": ContainsSchema,
        "StringNotContains": NotContainsSchema,
        "StringEndsWith": EndsWithSchema,
        "StringStartsWith": StartsWithSchema,
        "StringMatchesRegex": RegexMatchSchema,
        "StringNotEndsWith": NotEndsWithSchema,
        "StringNotStartsWith": NotStartsWithSchema,

        "NumericEquals": EqSchema,
        "NumericNotEquals": NeqSchema,
        "NumericLessThan": LtSchema,
        "NumericLessThanEquals": LteSchema,
        "NumericGreaterThan": GtSchema,
        "NumericGreaterThanEquals": GteSchema,

        "DateEquals": DateEqSchema,
        "DateNotEquals": DateNeqSchema,
        "DateLessThan": DateLtSchema,
        "DateLessThanEquals": DateLteSchema,
        "DateGreaterThan": DateGtSchema,
        "DateGreaterThanEquals": DateGteSchema,

        "Bool": CheckBoolSchema,

        "IpAddress": InSubnetSchema,
        "NotIpAddress": NotInSubnetSchema,

        "ListAllIn": AllInSchema,
        "ListAllNotIn": AllNotInSchema,
        "ListAnyIn": AnyInSchema,
        "ListAnyNotIn": AnyNotInSchema,
        "ListIsEmpty": IsEmptySchema,
        "ListIsIn": IsInSchema,
        "ListIsNotEmpty": IsNotEmptySchema,
        "ListIsNotIn": IsNotInSchema,

        "DayEquals": DayEqSchema,
        "DayNotEquals": DayNeqSchema,
        "DayLessThan": DayLtSchema,
        "DayLessThanEquals": DayLteSchema,
        "DayGreaterThan": DayGtSchema,
        "DayGreaterThanEquals": DayGteSchema,

        "Exists": ExistsSchema,
        "NotExists": NotExistsSchema,

    }

    class Meta:
        unknown = EXCLUDE

