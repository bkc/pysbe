"""test_fix_parser.py - test fix_parser"""
import os
import pytest

from pysbe.parser.fix_parser import SBESpecParser

class TestFixParser:

    def test_parse_invalid_xml(self, test_data_dir, filename='invalid_sample1.xml'):
        """parse this xml file"""
        sbe = SBESpecParser()
        with pytest.raises(ValueError):
            sbe.parseFile(
                os.path.join(
                    test_data_dir,
                    filename,
                )
            )


    def test_parse_xml(self, test_data_dir, filename='basic_sample1.xml'):
        """parse this xml file"""
        sbe = SBESpecParser()
        sbe.parseFile(
            os.path.join(
                test_data_dir,
                filename,
            )
        )

        assert sbe.parse_ok
