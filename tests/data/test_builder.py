"""test_builder.py - test schema.builder"""
import pytest

from pysbe.schema.builder import createMessageSchema
from pysbe.schema.constants import SBE_BYTE_ORDER


class TestBuilder:

    def test_invalid_version(self):
        """create message w/ invalid version"""
        with pytest.raises(ValueError):
            createMessageSchema(
                version=None
            )
        with pytest.raises(ValueError):
            createMessageSchema(
                version=-1
            )
        with pytest.raises(ValueError):
            createMessageSchema(
                version='1'
            )

    def test_invalid_package(self):
        """create message invalid package"""
        with pytest.raises(ValueError):
            createMessageSchema(
                version=0,
                package=1,
            )
        with pytest.raises(ValueError):
            createMessageSchema(
                version=0,
                package=1.0,
            )

    def test_invalid_schema_id(self):
        """create message invalid schema_id"""
        with pytest.raises(ValueError):
            createMessageSchema(
                version=0,
                schema_id="invalid",
            )
        with pytest.raises(ValueError):
            createMessageSchema(
                version=0,
                schema_id=1.0,
            )
        with pytest.raises(ValueError):
            createMessageSchema(
                version=0,
                schema_id=-1,
            )
        with pytest.raises(ValueError):
            createMessageSchema(
                version=0,
                schema_id=1000000,
            )

    def test_invalid_byteOrder(self):
        """create message invalid schema_id"""
        with pytest.raises(ValueError):
            createMessageSchema(
                version=0,
                byteOrder="hi",
            )

    def test_valid_byteOrder(self):
        """test valid byte order"""
        createMessageSchema(
            version=0,
            byteOrder=SBE_BYTE_ORDER.BIG_ENDIAN
        )
