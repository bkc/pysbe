"""constants.py - values used by parser and other components"""
import enum

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
    enum_value = enum.Enum(
        enum_name,
        value_map,
    )

    string_map = {
        s: getattr(enum_value, v)
        for v, s in value_map.items()
    }
    return enum_value, string_map


SBE_BYTE_ORDER, SBE_STRING_ENUM_MAP = make_enum_and_map(
    'SBE_BYTE_ORDER',
    {
        'BIG_ENDIAN': 'bigEndian',
        'LITTLE_ENDIAN': 'littleEndian',
    }
)

VALID_SBE_BYTE_ORDER = SBE_STRING_ENUM_MAP.values()
