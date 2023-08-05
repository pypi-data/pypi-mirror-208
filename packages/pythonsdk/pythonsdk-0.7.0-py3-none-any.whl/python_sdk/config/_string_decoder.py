import base64
import functools
import json
import pathlib
import typing

from python_sdk.config import _config_value_types

ENCODED_STRING_LIST_SEPARATOR = ","

_T = typing.TypeVar("_T")


def _str_to_bool(string: str) -> bool:
    normalized_string = string.strip().lower()
    if normalized_string in {"true", "yes", "y", "1", "on"}:
        return True
    elif normalized_string in {"false", "no", "n", "0", "off"}:
        return False
    raise ValueError()


def _str_to_dict(string: str) -> dict[str, typing.Any]:
    try:
        data = json.loads(string)
    except json.JSONDecodeError:
        raise ValueError()

    if not isinstance(data, dict):
        raise ValueError()

    return data


def _str_to_base64_encoded_string(string: str) -> str:
    string = string.strip()
    if not string:
        raise ValueError()
    try:
        base64.b64decode(string, validate=True).decode("utf-8")  # check it can be decoded
    except Exception as e:
        raise ValueError() from e
    return string


def _str_to_literal(string: str, literal: type) -> str:
    string = string.strip()
    if string not in typing.get_args(literal):
        raise ValueError()
    return string


def _str_to_list_of_strs(string: str) -> list[str]:
    string = string.strip().strip(ENCODED_STRING_LIST_SEPARATOR)
    if not string:
        raise ValueError()
    return string.split(ENCODED_STRING_LIST_SEPARATOR)


def _str_to_list_of_ints(string: str) -> list[int]:
    string = string.strip().strip(ENCODED_STRING_LIST_SEPARATOR)
    if not string:
        raise ValueError()
    return [int(i) for i in string.split(ENCODED_STRING_LIST_SEPARATOR)]


def _str_to_list_of_floats(string: str) -> list[float]:
    string = string.strip().strip(ENCODED_STRING_LIST_SEPARATOR)
    if not string:
        raise ValueError()
    return [float(i) for i in string.split(ENCODED_STRING_LIST_SEPARATOR)]


def _str_to_list_of_base64_encoded_strings(string: str) -> list[str]:
    string = string.strip().strip(ENCODED_STRING_LIST_SEPARATOR)
    if not string:
        raise ValueError()
    maybe_base64_encoded_strings = string.split(ENCODED_STRING_LIST_SEPARATOR)
    for i in maybe_base64_encoded_strings:
        # check they can be decoded
        _str_to_base64_encoded_string(string=i)
    return maybe_base64_encoded_strings


def _str_to_list_of_paths(string: str) -> list[pathlib.Path]:
    if not string:
        raise ValueError()
    return [pathlib.Path(path) for path in string.split(ENCODED_STRING_LIST_SEPARATOR)]


def _str_to_list_of_literals(string: str, literal: type) -> list[str]:
    string = string.strip().strip(ENCODED_STRING_LIST_SEPARATOR)
    if not string:
        raise ValueError()
    strings = string.split(ENCODED_STRING_LIST_SEPARATOR)
    literal_options = typing.get_args(literal)
    for string in strings:
        if string not in literal_options:
            raise ValueError()
    return strings


def _get_string_decoder(data_type: type) -> typing.Callable[[str], _config_value_types.ConfigValueType]:
    # primitives
    if data_type == str:
        return str
    elif data_type == int:
        return int
    elif data_type == float:
        return float
    elif data_type == bool:
        return _str_to_bool
    elif getattr(data_type, "__origin__", None) == dict:
        return _str_to_dict
    elif data_type == _config_value_types.Base64EncodedString:
        return _str_to_base64_encoded_string
    elif data_type == pathlib.Path:
        return pathlib.Path
    elif _is_literal(data_type=data_type):
        return functools.partial(_str_to_literal, literal=data_type)

    # lists of primitives
    elif data_type == list[str]:
        return _str_to_list_of_strs
    elif data_type == list[int]:
        return _str_to_list_of_ints
    elif data_type == list[float]:
        return _str_to_list_of_floats
    elif data_type == list[_config_value_types.Base64EncodedString]:
        return _str_to_list_of_base64_encoded_strings
    elif data_type == list[pathlib.Path]:
        return _str_to_list_of_paths
    elif _is_list_of_literals(data_type=data_type):
        return functools.partial(_str_to_list_of_literals, literal=typing.get_args(data_type)[0])
    else:
        raise NotImplementedError("Datatype not supported.")


def _is_literal(data_type: type) -> bool:
    # For a type to be considered Literal it must be a typing.Literal with all arguments of type str
    if typing.get_origin(data_type) == typing.Literal:
        literal_options = list(typing.get_args(data_type))
        if len({type(arg) for arg in literal_options}) == 1 and type(literal_options[0]) == str:
            return True
    return False


def _is_list_of_literals(data_type: type) -> bool:
    return typing.get_origin(data_type) == list and _is_literal(data_type=typing.get_args(data_type)[0])


def type_is_supported(data_type: type) -> bool:
    try:
        _get_string_decoder(data_type=data_type)
        return True
    except NotImplementedError:
        return False


def decode_string(
    string: str, data_type: type[_config_value_types.ConfigValueType]
) -> _config_value_types.ConfigValueType:
    decoder = _get_string_decoder(data_type=data_type)
    return decoder(string)
