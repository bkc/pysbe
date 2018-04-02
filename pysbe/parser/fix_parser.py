"""fix_parser.py - parse V1.0 fixprotocol sbe xml files described 
    by xsd https://github.com/FIXTradingCommunity/fix-simple-binary-encoding/blob/master/v1-0-STANDARD/resources/sbe.xsd
"""
import xml.etree.ElementTree as etree

SBE_NS = 'http://fixprotocol.io/2016/sbe'

class SBESpecParser:
    """Parser for VFIX"""
    NS = {
        'sbe': SBE_NS,
    }
    def __init__(self):
        self.parse_ok = False

    def parseFile(self, file_or_object):
        """parse a file"""
        root = etree.parse(file_or_object)
        element_name = '{%s}messageSchema' % SBE_NS
        # for some reason root.find('sbe:messageSchema') returns None
        # work around that
        first_element = root.getroot()
        if first_element.tag != element_name:
            raise ValueError(
                f"root element is not sbe:messageSchema, found {repr(first_element)} instead"
            )
        self.processSchema(first_element)
        

    def processSchema(self, messageSchema):
        """process xml elements beginning with root messageSchema"""
        attrib = messageSchema.attrib
        print(f'found attributes {repr(attrib)}')
        
