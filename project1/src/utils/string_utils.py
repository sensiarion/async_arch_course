import re


def to_camel(val: str):
    return ''.join([part.lower() if i == 0 else part.capitalize() for i, part in enumerate(val.split('_'))])


def to_snake(string: str) -> str:
    """
    Из CamelCase в snake_case
    """
    return re.sub('(?!^)([A-Z]+)', r'_\1', string).lower()


def trim_string(val: str, max_length: int) -> str:
    """
    Trim any string exceeds specified length with dots on end
    """
    length = len(val)
    if length > max_length:
        val = val[:max_length - 3] + '...'

    return val
