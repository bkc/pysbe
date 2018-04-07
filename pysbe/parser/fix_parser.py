"""fix_parser.py - parse V1.0 fixprotocol sbe xml files described
    by xsd https://github.com/FIXTradingCommunity/
    fix-simple-binary-encoding/blob/master/v1-0-STANDARD/resources/sbe.xsd
"""
import xml.etree.ElementTree as etree

from pysbe.schema.constants import (
    SBE_TYPES_TYPE,
    SBE_STRING_ENUM_MAP,
)
from pysbe.schema.builder import createMessageSchema

SBE_NS = 'http://fixprotocol.io/2016/sbe'


class SBESpecParser:
    """Parser for VFIX"""
    NS = {
        'sbe': SBE_NS,
    }

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
            attrib.get('byteOrder')
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
            attrib.get('headerType')
        )
        messageSchema = createMessageSchema(
            version=version,
            byteOrder=byteOrder,
            package=package,
            semanticVersion=semanticVersion,
            description=description,
            headerType=headerType,
        )

        types_element = messageSchema_element.findall(
            'sbe:types',
            namespaces=self.NS,
        )

        print(f'types {repr(types_element)}\n')
        return messageSchema


def parse_byteOrder(byteOrder):
    """convert byteOrder to enum"""
    if byteOrder is None or byteOrder == "":
        return None

    value = SBE_STRING_ENUM_MAP.get(byteOrder)
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
