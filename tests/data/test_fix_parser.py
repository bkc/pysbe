"""test_fix_parser.py - test fix_parser"""
import os
import pytest

from pysbe.parser.fix_parser import (
    SBESpecParser,
    parse_byteOrder,
    parse_version,
    parse_optionalString,
)

from pysbe.schema.constants import (
    BYTE_ORDER
)

from pysbe.schema.builder import (
    MessageSchema
)


class TestFixParser:

    def test_parse_invalid_byteorder(self):
        with pytest.raises(ValueError):
            parse_byteOrder('low')

    def test_parse_valid_byteorder(self):
        assert parse_byteOrder('') == None  # noqa: E711
        assert parse_byteOrder(None) == None  # noqa: E711
        assert parse_byteOrder('bigEndian') == BYTE_ORDER.BIG_ENDIAN
        assert parse_byteOrder('littleEndian') == BYTE_ORDER.LITTLE_ENDIAN

    def test_parse_opt_string(self):
        assert parse_optionalString('ok') == 'ok'
        assert parse_optionalString('') == None  # noqa: E711
        assert parse_optionalString(None) == None  # noqa: E711

    def test_parse_version(self):
        with pytest.raises(ValueError):
            parse_version(None)
        with pytest.raises(ValueError):
            parse_version('a')

    def test_parse_invalid_xml(
        self,
        test_data_dir,
        filename='invalid_sample1.xml'
    ):
        """parse this xml file"""
        sbe = SBESpecParser()
        with pytest.raises(ValueError):
            sbe.parseFile(
                os.path.join(
                    test_data_dir,
                    filename,
                )
            )

    def test_parse_invalid_types1(
        self,
        test_data_dir,
        filename='invalid_types_sample1.xml'
    ):
        """parse this xml file"""
        sbe = SBESpecParser()
        with pytest.raises(ValueError):
            sbe.parseFile(
                os.path.join(
                    test_data_dir,
                    filename,
                )
            )

    def test_parse_invalid_types2(
        self,
        test_data_dir,
        filename='invalid_types_sample2.xml'
    ):
        """parse this xml file"""
        sbe = SBESpecParser()
        with pytest.raises(ValueError):
            sbe.parseFile(
                os.path.join(
                    test_data_dir,
                    filename,
                )
            )


    def test_parse_xml(
        self,
        test_data_dir,
        filename='basic_sample1.xml'
    ):
        """parse this xml file"""
        sbe = SBESpecParser()
        messageSchema = sbe.parseFile(
            os.path.join(
                test_data_dir,
                filename,
            )
        )

        assert isinstance(messageSchema, MessageSchema)
