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
from pysbe.schema.types import (
    createType,
    createComposite,
    createEnum,
    createValidValue,
    TypeCollection,
    createRef,
    createSet,
    createChoice,
)
from pysbe.schema.exceptions import UnknownReference

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

ENUM_ATTRIBUTES = {
    'encodingType': {
        'type': str,
        'pattern': SYMBOLIC_NAME_RE,
    },
}

REF_ATTRIBUTES = {
    'type': {
        'type': str,        
    }
}

ALL_ATTRIBUTES_MAP = {
    **SEMANTIC_ATTRIBUTES,
    **VERSION_ATTRIBUTES,
    **ALIGNMENT_ATTRIBUTES,
    **PRESENCE_ATTRIBUTES,
    **TYPE_ATTRIBUTES,
    **ENUM_ATTRIBUTES,
    **REF_ATTRIBUTES,
}

TYPE_ATTRIBUTES_LIST = list(SEMANTIC_ATTRIBUTES) + \
    list(VERSION_ATTRIBUTES) + \
    list(ALIGNMENT_ATTRIBUTES) + \
    list(PRESENCE_ATTRIBUTES) + \
    list(TYPE_ATTRIBUTES)

COMPOSITE_ATTRIBUTES_LIST = ['name'] + \
list(SEMANTIC_ATTRIBUTES) + \
list(ALIGNMENT_ATTRIBUTES) + \
list(VERSION_ATTRIBUTES)

ENUM_ATTRIBUTES_LIST = ['name'] + \
    list(ENUM_ATTRIBUTES) + \
    list(ALIGNMENT_ATTRIBUTES) + \
    list(SEMANTIC_ATTRIBUTES) + \
    list(VERSION_ATTRIBUTES)

ENUM_VALID_VALUES_ATTRIBUTES_LIST = (
    'name',
    'description',
    'sinceVersion',
    'deprecated',
)

REF_ATTRIBUTES_LIST = (
    'name',
    'type',
    'offset',
    'sinceVersion',
    'deprecated',
)

SET_ATTRIBUTES_LIST = (
    'name',
    'description',
    'encodingType',
    'sinceVersion',
    'deprecated',
    'offset',
)

SET_CHOICE_ATTRIBUTES_LIST = (
    'name',
    'description',
    'sinceVersion',
    'deprecated',
)

VALID_COMPOSITE_CHILD_ELEMENTS = (
    'type',
    'enum',
    'set',
    'composite',
    'ref',
)

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
            self.parse_types(messageSchema, element)

        return messageSchema

    def parse_types(self, messageSchema, element):
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

            parser(messageSchema, child_element)

    def parse_types_type(self, parent: TypeCollection, element):
        """parse types/type"""
        attributes = self.parse_common_attributes(
            element,
            attributes=TYPE_ATTRIBUTES_LIST,
        )

        sbe_type = createType(**attributes)
        parent.addType(sbe_type)

    def parse_types_ref(self, parent: TypeCollection, element):
        """parse composite / ref"""
        attributes = self.parse_common_attributes(
            element,
            attributes=REF_ATTRIBUTES_LIST,
        )

        sbe_ref = createRef(**attributes)
        reference_type = parent.lookupName(
            sbe_ref.type
        )
        if not reference_type:
            raise UnknownReference(
                f"composite {parent.name} ref {sbe_ref.name} references unknown encodingType {sbe_ref.type}"
            )
        parent.addType(sbe_ref)


    def parse_types_composite(self, parent: TypeCollection, element):
        """parse types/composite"""
        attributes = self.parse_common_attributes(
            element,
            attributes=COMPOSITE_ATTRIBUTES_LIST,
        )

        sbe_composite = createComposite(**attributes)
        parent.addType(sbe_composite)

        # now iterate over composite children
        for child_element in element:
            tag = child_element.tag
            if tag not in VALID_COMPOSITE_CHILD_ELEMENTS:
                raise ValueError(
                    f'invalid child element {repr(tag)} in composite element {repr(sbe_composite.name)}'
                )

            parser = getattr(
                self,
                f'parse_types_{tag}',
                None,
            )
            if not parser:
                raise RuntimeError(
                    f'unsupported types parser {repr(child_element.tag)}'
                )

            parser(sbe_composite, child_element)

    def parse_types_set(self, parent: TypeCollection, element):
        """parse types/set"""
        attributes = self.parse_common_attributes(
            element,
            attributes=SET_ATTRIBUTES_LIST,
        )

        sbe_set = createSet(**attributes)
        parent.addType(sbe_set)
        for child_element in element.findall('choice'):
            choice = self.parse_set_choice(
                sbe_set=sbe_set,
                element=child_element,
            )
            sbe_set.addChoice(choice)
        
    def parse_set_choice(self, sbe_set, element):
        """parse and return an enum validvalue"""
        attributes = self.parse_common_attributes(
            element,
            attributes=SET_CHOICE_ATTRIBUTES_LIST,
        )
        value = element.text
        try:
            value = int(element.text)
        except ValueError as exc:
            raise ValueError(
                f"invalid value for set {sbe_set.name} choice {attributes.get('name')}"
            ) from exc
        choice = createChoice(
            value=value,
            **attributes
        )
        return choice

    def parse_types_enum(self, parent: TypeCollection, element):
        """parse types/enum"""
        attributes = self.parse_common_attributes(
            element,
            attributes=ENUM_ATTRIBUTES_LIST,
        )

        sbe_enum = createEnum(**attributes)
        parent.addType(sbe_enum)
        for child_element in element.findall('validValue'):
            valid_value = self.parse_enum_valid_value(
                sbe_enum=sbe_enum,
                element=child_element,
            )
            sbe_enum.addValidValue(valid_value)

    def parse_enum_valid_value(self, sbe_enum, element):
        """parse and return an enum validvalue"""
        attributes = self.parse_common_attributes(
            element,
            attributes=ENUM_VALID_VALUES_ATTRIBUTES_LIST,
        )
        value = element.text
        enum_valid_value = createValidValue(
            value=value,
            **attributes
        )
        return enum_valid_value



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
