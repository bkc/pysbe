"""constants.py - values used by parser and other components"""
import enum
import re

SYMBOLIC_NAME_RE = re.compile(
    r'([A-Z]|[a-z]|_)([0-9]|[A-Z]|[a-z]|_)*'
)

QUALIFIED_NAME_RE = re.compile(
    r'([A-Z]|[a-z]|_)([0-9]|[A-Z]|[a-z]|_)*\.([A-Z]|[a-z]|_)([0-9]|[A-Z]|[a-z]|_)*'
)

SBE_TYPES_TYPE = enum.Enum(
    'SBE_TYPES_TYPE',
    {
        'TYPE': 'type',
        'COMPOSITE': 'composite',
        'ENUM': 'enum',
        'SET': 'set',
    },
)

def make_enum_and_map(
        enum_name,
        value_map):
    """return enum, mapping from string to enums"""

    if isinstance(value_map, (list, tuple)):
        # generate a map by upper casing list
        keys = [x.upper() for x in value_map]
        value_map = dict(zip(keys, value_map))

    enum_value = enum.Enum(
        enum_name,
        value_map,
    )

    string_map = {
        s: getattr(enum_value, v)
        for v, s in value_map.items()
    }
    return enum_value, string_map


BYTE_ORDER, STRING_ENUM_MAP = make_enum_and_map(
    'BYTE_ORDER',
    {
        'BIG_ENDIAN': 'bigEndian',
        'LITTLE_ENDIAN': 'littleEndian',
    }
)

VALID_BYTE_ORDER = STRING_ENUM_MAP.values()
PRIMITIVE_TYPE_LIST = (
    "char",
    "int8",
    "int16",
    "int32",
    "int64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "float",
    "double",
)

TYPE_PRIMITIVE_TYPE, TYPE_PRIMITIVE_TYPE_MAP = make_enum_and_map(
    'TYPE_PRIMITIVE_TYPE',
    PRIMITIVE_TYPE_LIST,
)

VALID_TYPE_PRIMITIVE_TYPE = TYPE_PRIMITIVE_TYPE_MAP.keys()

PRESENCE, PRESENCE_MAP = make_enum_and_map(
    'PRESENCE',
    (
        "required",
        "optional",
        "constant",
    )
)

VALID_PRESENCE = PRESENCE_MAP.keys()

