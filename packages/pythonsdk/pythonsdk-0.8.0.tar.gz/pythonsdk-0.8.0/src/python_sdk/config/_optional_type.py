import types
import typing


def is_optional_type(data_type: type) -> bool:
    return (
        typing.get_origin(data_type) in [types.UnionType, typing.Union]
        and len(typing.get_args(data_type)) == 2
        and types.NoneType in typing.get_args(data_type)
    )


def get_type_in_optional_type(data_type: type) -> type:
    return [type_ for type_ in typing.get_args(data_type) if type_ is not types.NoneType][0]  # type: ignore
