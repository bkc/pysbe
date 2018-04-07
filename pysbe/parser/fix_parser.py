"""fix_parser.py - parse V1.0 fixprotocol sbe xml files described
    by xsd https://github.com/FIXTradingCommunity/
    fix-simple-binary-encoding/blob/master/v1-0-STANDARD/resources/sbe.xsd
"""
import xml.etree.ElementTree as etree

from pysbe.schema.constants import (
    SBE_TYPES_TYPE,
    STRING_ENUM_MAP,
    VALID_TYPE_PRIMITIVE_TYPE,
    TYPE_PRIMITIVE_TYPE_MAP,
    PRESENCE_MAP,
    QUALIFIED_NAME_RE,
    SYMBOLIC_NAME_RE,
)
from pysbe.schema.builder import createMessageSchema
from pysbe.schema.types import createType

SBE_NS = 'http://fixprotocol.io/2016/sbe'

SEMANTIC_ATTRIBUTES = {
    'semanticType': {
        'type': str,
        'use': 'optional',
    },
    'description': {
        'type': str,
        'use': 'optional',
    },
}

VERSION_ATTRIBUTES = {
    'sinceVersion': {
        'type': int,
        'default': 0,
        'minimumValue': 0,
        'use': 'optional',
    },
    # deprecated is itself deprecated in RC4
    'deprecated': {
        'type': int,
        'minimumValue': 0,
        'use': 'optional',
    },
}

ALIGNMENT_ATTRIBUTES = {
    'offset': {
        'type': int,
        'minimumValue': 0,
        'use': 'optional',
    },
}

PRESENCE_ATTRIBUTES = {
    'presence': {
        'type': str,
        'default': 'required',
        'map': PRESENCE_MAP,
    },
    'valueRef': {
        'type': str,
        'use': 'optional',
        'pattern': QUALIFIED_NAME_RE,
    },
}

TYPE_ATTRIBUTES = {
    'name': {
        'type': str,
        'pattern': SYMBOLIC_NAME_RE,
    },
    'primitiveType': {
        'type': str,
        'map': TYPE_PRIMITIVE_TYPE_MAP,
    },
    'nullValue': {
        'type': str,
        'use': 'optional',
    },
    'minValue': {
        'type': str,
        'use': 'optional',
    },
    'maxValue': {
        'type': str,
        'use': 'optional',
    },
    'characterEncoding': {
        'type': str,
        'use': 'optional',
    },
    'length': {
        'type': int,
        'minimumValue': 0,
        'use': 'optional',
        'default': 1,
    },
}

ALL_ATTRIBUTES_MAP = {
    **SEMANTIC_ATTRIBUTES,
    **VERSION_ATTRIBUTES,
    **ALIGNMENT_ATTRIBUTES,
    **PRESENCE_ATTRIBUTES,
    **TYPE_ATTRIBUTES,
}

TYPE_ATTRIBUTES_LIST = list(ALL_ATTRIBUTES_MAP) + list(TYPE_ATTRIBUTES)

MISSING = object()

class SBESpecParser:
    """Parser for VFIX"""
    NS = {
        'sbe': SBE_NS,
    }

    # which child elements may appear in types
    VALID_TYPES_ELEMENTS = (
        'type',
        'composite',
        'enum',
        'set',
    )
    def __init__(self):
        pass

    def parseFile(self, file_or_object):
        """parse a file"""
        root = etree.parse(file_or_object)
        element_name = '{%s}messageSchema' % SBE_NS
        # for some reason root.find('sbe:messageSchema') returns None
        # work around that
        messageSchema_element = root.getroot()
        if messageSchema_element.tag != element_name:
            raise ValueError(
                f"root element is not sbe:messageSchema,"
                " found {repr(messageSchema_element)} instead"
            )
        return self.processSchema(messageSchema_element)

    def processSchema(self, messageSchema_element):
        """process xml elements beginning with root messageSchema_element"""
        attrib = messageSchema_element.attrib
        print(f'found attributes {repr(attrib)}')
        version = parse_version(
            attrib.get('version')
        )
        byteOrder = parse_byteOrder(
            attrib.get('byteOrder') or 'littleEndian'
        )
        package = parse_optionalString(
            attrib.get('package')
        )
        semanticVersion = parse_optionalString(
            attrib.get('semanticVersion')
        )
        description = parse_optionalString(
            attrib.get('description')
        )
        headerType = parse_optionalString(
            attrib.get('headerType') or 'messageHeader'
        )
        messageSchema = createMessageSchema(
            version=version,
            byteOrder=byteOrder,
            package=package,
            semanticVersion=semanticVersion,
            description=description,
            headerType=headerType,
        )

        types_elements = messageSchema_element.findall(
            'types',
        )

        for element in types_elements:
            self.parse_types(element)

        return messageSchema

    def parse_types(self, element):
        """parse type, can be repeated"""
        for child_element in element:
            if child_element.tag not in self.VALID_TYPES_ELEMENTS:
                raise ValueError(
                    f'invalid types child element {repr(child_element.tag)}'
                )

            parser = getattr(
                self,
                f'parse_types_{child_element.tag}',
                None,
            )
            if not parser:
                raise RuntimeError(
                    f'unsupported types parser {repr(child_element.tag)}'
                )

            parser(child_element)

    def parse_types_type(self, element):
        """parse types/type"""
        attrib = element.attrib
        name = attrib.get('name')
        if not name:
            raise ValueError(
                "type element missing required 'name' attribute"
            )
        primitiveType = attrib.get('primitiveType')
        if not primitiveType:
            raise ValueError(
                f"type element missing required 'primitiveType' attribute"
            )
        if primitiveType not in VALID_TYPE_PRIMITIVE_TYPE:
            raise ValueError(
                f"type element has invalid primitiveType {repr(primitiveType)}"
                f"expected one of {VALID_TYPE_PRIMITIVE_TYPE}"
            )

        attributes = self.parse_common_attributes(
            element,
            attributes=TYPE_ATTRIBUTES_LIST,
        )

        sbe_type = createType(**attributes)

    def parse_common_attributes(
            self,
            element,
            attributes):
        """parse and return dict of common attributes"""
        result_attributes = {}
        for attribute in attributes:
            attrib_info = ALL_ATTRIBUTES_MAP[attribute]
            if attrib_info.get('default', MISSING) is not MISSING:
                default_value = attrib_info['default']
            else:
                default_value = MISSING
            value = element.attrib.get(attribute, default_value)
            if value is MISSING or value == '':
                if attrib_info.get('use') == 'optional':
                    continue
                else:
                    raise ValueError(
                        f'element {element.tag} missing required attribute {attribute}'
                    )
            if attrib_info.get('type'):
                try:
                    value = attrib_info['type'](value)
                except ValueError as exc:
                    raise ValueError(
                        f'element {element.tag} invalid value {repr(value)} for attribute {attribute}'
                    ) from exc

            if attrib_info.get('minimumValue'):
                if value < attrib_info['minimumValue']:
                    raise ValueError(
                        f'element {element.tag} invalid value {repr(value)} for attribute {attribute}'
                        f", less than allowed minimum {repr(attrib_info['minimumValue'])}"
                    )
            if attrib_info.get('pattern'):
                if not attrib_info['pattern'].match(value):
                    raise ValueError(
                        f'element {element.tag} invalid value {repr(value)} for attribute {attribute}'
                        f", does not match expected pattern {repr(attrib_info['pattern'])}"
                    )
            if attrib_info.get('map'):
                try:
                    value = attrib_info['map'][value]
                except (KeyError, IndexError) as exc:
                    raise ValueError(
                        f'element {element.tag} invalid value {repr(value)} for attribute {attribute}'
                        f", must be one of {repr(attrib_info['map'].keys())}"
                    ) from exc

            result_attributes[attribute] = value

        return result_attributes

def parse_byteOrder(byteOrder):
    """convert byteOrder to enum"""
    if byteOrder is None or byteOrder == "":
        return None

    value = STRING_ENUM_MAP.get(byteOrder)
    if value is None:
        raise ValueError(
            f'invalid byteOrder {repr(value)},'
            'expected one of {SBE_STRING_ENUM_MAP.keys()}'
        )

    return value


def parse_version(version):
    """convert version to int"""
    if version is None:
        raise ValueError('sbe:messageSchema/@version is required')

    return int(version)


def parse_optionalString(value):
    """parse an optional string"""
    if not value:
        return None
    
    return value
