from __future__ import annotations

import base64
import collections.abc
from datetime import date, datetime, time, timedelta
from typing import Any, List, Optional, Type, Union, cast

import cattrs
import dateutil.parser
import isodate
from typing_extensions import get_args, get_origin, is_typeddict

from chalk.features._encoding.primitive import TPrimitive
from chalk.utils.cached_type_hints import cached_get_type_hints
from chalk.utils.json import TJSON

__all__ = ["unstructure_primitive_to_json", "structure_json_to_primitive"]


_json_converter = cattrs.Converter()


def unstructure_primitive_to_json(val: TPrimitive) -> TJSON:
    return _json_converter.unstructure(val)


def structure_json_to_primitive(val: Union[TJSON, TPrimitive], typ: Type[TPrimitive]) -> TPrimitive:
    return _json_converter.structure(val, typ)


#######
# Dicts
#######

# All structs get mapped to a typeddict primitive type
# However, on the wire, we serialize typedicts as lists by field order, similar
# to how structs are commonly serialized by values
# Hence, the JSON converter needs to convert all dicts into lists of the values
# In py3.7+, all dicts are ordered. So, simply iterating over the dict values is sufficient
_json_converter.register_unstructure_hook(dict, lambda x: [_json_converter.unstructure(y) for y in x.values()])


def _structure_typeddict(obj: Any, typ: Type):
    type_hints = cached_get_type_hints(typ)
    if obj is None:
        return {
            field_name: _json_converter.structure(None, type_hint) for (field_name, type_hint) in type_hints.items()
        }
    if isinstance(obj, collections.abc.Mapping):
        # If given a dict, assume it is the primitive type being passed in as the json type
        return {
            field_name: _json_converter.structure(obj.get(field_name), type_hint)
            for (field_name, type_hint) in type_hints.items()
        }
    if not isinstance(obj, collections.abc.Sequence):
        raise TypeError(f"Expected structs to be serialized as lists. Object `{obj}` is not a sequence.")

    if len(type_hints) != len(obj):
        raise TypeError(
            f"Unable to structure object `{obj}` of size {len(obj)} into type `{typ.__name__}` of size {len(type_hints)}. Size mismatch."
        )

    kwargs = {
        field_name: None if x is None else _json_converter.structure(x, type_hints[field_name])
        for (x, field_name) in zip(obj, type_hints.keys())
    }
    return kwargs


_json_converter.register_structure_hook_func(is_typeddict, _structure_typeddict)


#######
# Lists
#######

# The default unstructure hook is fine
# However, when structuring, we want to allow None for annotations of list[...]


def _structure_list(obj: Optional[List], typ: Type[List]) -> List:
    args = get_args(typ)

    if len(args) < 1:
        raise TypeError(
            f"{typ} types must be parameterized with the type of the contained value -- for example, `{typ}[int]`"
        )
    if len(args) > 1:
        raise TypeError(f"{typ} should be parameterized with only one type")
    if obj is None:
        return cast(List, None)
    if not isinstance(obj, (list, tuple)):
        raise TypeError(f"Expected a list, Object `{obj}` is not a list.")

    inner_typ = args[0]
    return [_json_converter.structure(x, inner_typ) for x in obj]


def _is_list(typ: Type):
    origin = get_origin(typ)
    return origin in (list, List)


_json_converter.register_structure_hook_func(_is_list, _structure_list)


######
# Date
######
def _is_date(x: Type):
    return isinstance(x, type) and issubclass(x, date) and not issubclass(x, datetime)


_json_converter.register_unstructure_hook_func(
    _is_date,
    lambda x: x.isoformat(),
)


def _structure_date(obj: Any, typ: Type):
    if isinstance(obj, datetime):
        return obj.date()
    if isinstance(obj, date):
        return obj
    if not isinstance(obj, str):
        raise TypeError(
            f"Date values must be serialized as ISO strings. Instead, received value '{obj}' of type `{type(obj).__name__}`"
        )
    return isodate.parse_date(obj)


_json_converter.register_structure_hook_func(
    _is_date,
    _structure_date,
)


##########
# Datetime
##########


_json_converter.register_unstructure_hook(datetime, lambda x: x.isoformat())


def _structure_datetime(obj: Any, typ: Type):
    if obj is None:
        return None
    if isinstance(obj, datetime):
        return obj
    if isinstance(obj, date):
        # Upgrade to a datetime
        return datetime.combine(obj, time())
    if not isinstance(obj, str):
        raise TypeError(
            f"Datetime values must be serialized as ISO strings. Instead, received value '{obj}' of type `{type(obj).__name__}`"
        )
    return dateutil.parser.parse(obj)


_json_converter.register_structure_hook(datetime, _structure_datetime)

######
# Time
######

_json_converter.register_unstructure_hook(time, lambda x: x.isoformat())


def _structure_time(obj: Any, typ: Type):
    if obj is None:
        return None
    if isinstance(obj, time):
        return obj
    if not isinstance(obj, str):
        raise TypeError(
            f"Time values must be serialized as ISO strings. Instead, received value '{obj}' of type `{type(obj).__name__}`"
        )
    return isodate.parse_time(obj)


_json_converter.register_structure_hook(time, _structure_time)

########
# Binary
########

_json_converter.register_unstructure_hook(bytes, lambda x: base64.b64encode(x).decode("utf8"))


def _structure_bytes(obj: Any, typ: Type):
    if obj is None:
        return None
    if isinstance(obj, str):
        return base64.b64decode(obj)
    if isinstance(obj, bytes):
        return obj
    raise TypeError(
        f"Byte values must be bytes objects or Base64-encoded strings. Instead, received value '{obj}' of type `{type(obj).__name__}`"
    )


_json_converter.register_structure_hook(bytes, _structure_bytes)

_json_converter.register_unstructure_hook(timedelta, isodate.duration_isoformat)

###########
# Timedelta
###########


def _structure_timedelta(obj: Any, typ: Type):
    if obj is None:
        return None
    if isinstance(obj, timedelta):
        return obj
    if not isinstance(obj, str):
        raise TypeError(
            f"Timedelta values should be serialized as strings. Instead, received value '{obj}' of type `{type(obj).__name__}`"
        )
    return isodate.parse_duration(obj)


_json_converter.register_structure_hook(timedelta, _structure_timedelta)

####################
# Int/float/str/bool
####################


def _structure_basic(obj: Any, typ: Type):
    if obj is None:
        # Always allow None, even if the field is non-optional
        return None
    if issubclass(typ, bool):
        # For booleans, we are more strict than just doing a simple cast, since
        # bool("random string") or bool(100) should raise an exception, not be True
        if obj in (1, True):
            return True
        if obj in (0, False):
            return False
        raise TypeError(f"Cannot convert '{obj}' to a Boolean. Valid values are 1, True, 0, or False.")
    if issubclass(typ, (int, float)):
        if typ(obj) != obj:
            raise TypeError(f"Cannot cast '{obj}' to a {typ} without losing precision")
    return typ(obj)


_json_converter.register_structure_hook(int, _structure_basic)
_json_converter.register_structure_hook(float, _structure_basic)
_json_converter.register_structure_hook(str, _structure_basic)
_json_converter.register_structure_hook(bool, _structure_basic)
