from typing import Any

TRUE_VALUES = {'y', 'yes', 't', 'true', 'on', '1', '+'}
FALSE_VALUES = {'n', 'no', 'f', 'false', 'off', '0', '-', ''}


def serialize_to_boolean(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    value = str(value).lower()

    if value in TRUE_VALUES:
        return True

    if value in FALSE_VALUES:
        return False

    return default
