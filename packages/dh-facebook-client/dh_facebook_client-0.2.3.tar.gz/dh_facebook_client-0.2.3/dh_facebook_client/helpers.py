from datetime import datetime
from typing import Any, Callable, Final, Iterable, Optional

from typing_extensions import NotRequired, TypedDict

# TODO: Recursive type hints not yet available in mypy,
#  should change sub_fields hint to Optional[List[FieldConfig]] when possible:
#  https://github.com/python/mypy/issues/731
FieldConfig = TypedDict(
    'FieldConfig',
    {
        'field_name': str,
        'limit': NotRequired[int],
        'after': NotRequired[str],
        'date_preset': NotRequired[str],
        'sub_fields': NotRequired[list[Any]],
    },
)


ACCEPTED_SUB_PARAM_NAMES: Final = (
    'limit',
    'after',
    'date_preset',
)


def format_fields_str(fields_config: list[FieldConfig]) -> str:
    """
    Helper function to support field expansion / limiting functionality:
    https://developers.facebook.com/docs/graph-api/field-expansion
    :param fields_config: The field configurations you want contained in string format
    :return: A formatted fields string
    """
    fields_str = ''
    for config in fields_config:
        # Prep the base sub string for a field w/ params (i.e. foo.limit(5).after(BAR))
        fields_str += f'{config["field_name"]}'
        for param_name in ACCEPTED_SUB_PARAM_NAMES:
            fields_str += _format_sub_parameter_str(config, param_name)
        # If sub-fields exist, prep the nested sub-field(s) strings
        sub_fields = config.get('sub_fields')
        if sub_fields:
            fields_str += f'{{{format_fields_str(sub_fields)}}}'

        # If not the last item in a config list, add a comma separator
        if config != fields_config[-1]:
            fields_str += ','
    return fields_str


def _format_sub_parameter_str(config: FieldConfig, param_name: str) -> str:
    """
    Used to help format sub-param strings for a specific field:
    Ex: https://developers.facebook.com/docs/graph-api/field-expansion#limiting-results
    :param config: An instance of FieldConfig
    :param param_name: The parameter name to pluck from config (i.e. limit or after)
    :return: A formatted paging sub string (i.e. .limit(5))
    """
    param = config.get(param_name)
    return f'.{param_name}({param})' if param else ''


def posix_2_datetime(timestamp: int) -> datetime:
    """
    Convert POSIX timestamp to datetime
    :param timestamp: POSIX timestamp
    :return: Resulting datetime obj
    """
    return datetime.utcfromtimestamp(timestamp / 1000)


def first_true(
    iterable: Iterable[Any], pred: Callable, default: Optional[Any] = None
) -> Optional[Any]:
    """
    Find the first occurrence of something matching a predicate with default value
    :param iterable: Iterable containing items to match
    :param pred: Predicate containing matching logic
    :param default: Default value if no match found
    :return: Matching item or default
    """
    return next(filter(pred, iterable), default)
