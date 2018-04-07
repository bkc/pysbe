"""types.py - schema for types type, composite, enum, etc"""
from typing import Optional
from . constants import PRESENCE, TYPE_PRIMITIVE_TYPE

class BaseType:
    pass

class Type(BaseType):
    def __init__(
        self,
        name: [str],
        primitiveType: [TYPE_PRIMITIVE_TYPE],
        presence: [PRESENCE],
        description: Optional[str]=None,
        nullValue: Optional[str]=None,
        minValue: Optional[str]=None,
        maxValue: Optional[str]=None,
        length: int=1,
        offset: Optional[int]=None,
        semanticType: Optional[str]=None,
        sinceVersion: Optional[int]=0,
        deprecated: Optional[int]=None,
        characterEncoding: Optional[str]=None,
    ):
        pass


def createType(
        name: [str],
        primitiveType: [TYPE_PRIMITIVE_TYPE],
        presence: [PRESENCE],
        description: Optional[str]=None,
        nullValue: Optional[str]=None,
        minValue: Optional[str]=None,
        maxValue: Optional[str]=None,
        length: int=1,
        offset: Optional[int]=None,
        semanticType: Optional[str]=None,
        sinceVersion: Optional[int]=0,        
        deprecated: Optional[int]=None,
        characterEncoding: Optional[str]=None):
    """create a new Type"""
    sbeType = Type(
        name=name,
        description=description,
        presence=presence,
        nullValue=nullValue,
        minValue=minValue,
        maxValue=maxValue,
        length=length,
        offset=offset,
        semanticType=semanticType,
        primitiveType=primitiveType,
        sinceVersion=sinceVersion,
        deprecated=deprecated,
        characterEncoding=characterEncoding,
    )

    return sbeType


