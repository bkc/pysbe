"""builder.py - construct schema object"""
from typing import Optional

from . constants import (
    VALID_BYTE_ORDER,
)

from . types import Type

class MessageSchema:
    """describes an SBE messageSchema"""

    def __init__(
        self,
        version: int,
        package: Optional[str]=None,
        schema_id: Optional[int]=None,
        semanticVersion: Optional[str]=None,
        description: Optional[str]=None,
        byteOrder: Optional[str]=None,
        headerType: Optional[str]=None,
    ) -> None:
        if not isinstance(version, int) or version < 0:
            raise ValueError("version must be a positive integer")
        if package and not isinstance(package, str):
            raise ValueError("package must be None or a string")
        if schema_id and (
            not isinstance(schema_id, int) or
            schema_id < 0 or schema_id > 65535
        ):
            raise ValueError(
                'schema_id must be None or an integer between 0 and 65535'
            )
        if semanticVersion and not isinstance(semanticVersion, str):
            raise ValueError("semanticVersion must be None or a string")
        if description and not isinstance(description, str):
            raise ValueError("description must be None or a string")
        if byteOrder and byteOrder not in VALID_BYTE_ORDER:
            raise ValueError(
                "byteOrder must be None or one of %r" % VALID_BYTE_ORDER
            )
        if headerType and not isinstance(headerType, str):
            raise ValueError("headerType must be None or a string")
        self.version = version
        self.package = package
        self.schema_id = schema_id
        self.semanticVersion = semanticVersion
        self.description = description
        self.byteOrder = byteOrder
        self.headerType = headerType

        self.typesNameMap = {}

    def addType(self, sbeType):
        """add a new type"""
        pass

def createMessageSchema(
        version: int,
        package: Optional[str]=None,
        schema_id: Optional[int]=None,
        semanticVersion: Optional[str]=None,
        description: Optional[str]=None,
        byteOrder: Optional[str]=None,
        headerType: Optional[str]=None,
        ) -> MessageSchema:
    """create and return a new MessageSchema object"""
    messageSchema = MessageSchema(
        version=version,
        package=package,
        schema_id=schema_id,
        semanticVersion=semanticVersion,
        description=description,
        byteOrder=byteOrder,
        headerType=headerType,
    )

    return messageSchema
