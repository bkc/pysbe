"""types.py - schema for types type, composite, enum, etc"""
from typing import Optional, Union
from . constants import PRESENCE, TYPE_PRIMITIVE_TYPE
from . exceptions import DuplicateName

class TypeCollection:
    """Holds map of types"""
    def __init__(self, *args, **kw):
        self.typesNameMap = {}

    def addType(self,
        sbeType: Union[
            'Type',
            'Composite',
            'Enum'
        ]) -> None:
        """add a new type"""
        if sbeType.name in self.typesNameMap:
            raise DuplicateName(
                f'{sbeType.name}'' already registered in composite {self.name}')

        self.typesNameMap[sbeType.name] = sbeType

class BaseType:

    def __repr__(self):
        from pprint import pformat
        return f"{self.__class__.__name__}\n{pformat(vars(self), indent=8, width=1)}"

    def as_dict(self):
        """for debugging, return dict represenation"""
        d = self.__dict__.copy()
        d['__class__'] = self.__class__.__name__
        if 'typesNameMap' in d:
            d['typesNameMap'] = {
                key: value.as_dict()
                for key, value in d['typesNameMap'].items()
            }

        for key, value in d.items():
            if isinstance(value, list) and len(value) and hasattr(value[0], 'as_dict'):
                d[key] = [
                    x.as_dict()
                    for x in value
                ]
            elif isinstance(value, dict):
                d[key] = {
                    ikey: ivalue.as_dict() if hasattr(ivalue, 'as_dict') else ivalue
                    for ikey, ivalue in value.items()
                }
                
        return d


class Type(BaseType):
    """A primitive Type"""
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
        valueRef: Optional[str]=None,
    ) -> None:
        """initialize primitive type"""
        self.name = name
        self.description = description
        self.presence = presence
        self.nullValue = nullValue
        self.minValue = minValue
        self.maxValue = maxValue
        self.length = length
        self.offset = offset
        self.semanticType = semanticType
        self.primitiveType = primitiveType
        self.sinceVersion = sinceVersion
        self.deprecated = deprecated
        self.characterEncoding = characterEncoding
        self.valueRef = valueRef

        self.is_scalar = self.length == 1


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
        characterEncoding: Optional[str]=None,
        valueRef: Optional[str]=None,
    ) -> Type:
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
        valueRef=valueRef,
    )

    return sbeType


class Composite(BaseType, TypeCollection):
    """A composite type"""

    def __init__(
        self,
        name: [str],
        description: Optional[str]=None,
        offset: Optional[int]=None,
        semanticType: Optional[str]=None,
        sinceVersion: Optional[int]=0,
        deprecated: Optional[int]=None
    ) -> None:
        """initialize composite type"""
        super().__init__()
        self.name = name
        self.description = description
        self.offset = offset
        self.semanticType = semanticType
        self.sinceVersion = sinceVersion
        self.deprecated = deprecated


def createComposite(
        name: [str],
        description: Optional[str]=None,
        offset: Optional[int]=None,
        semanticType: Optional[str]=None,
        sinceVersion: Optional[int]=0,
        deprecated: Optional[int]=None
    ) -> Composite:
    """create a new Type"""
    composite = Composite(
        name=name,
        description=description,
        offset=offset,
        semanticType=semanticType,
        sinceVersion=sinceVersion,
        deprecated=deprecated,
    )

    return composite


class Enum(BaseType):
    """An Enum"""

    def __init__(
        self,
        name: [str],
        encodingType: Optional[str]=None,
        description: Optional[str]=None,
        offset: Optional[int]=None,
        semanticType: Optional[str]=None,
        sinceVersion: Optional[int]=0,
        deprecated: Optional[int]=None,
    ) -> None:
        """initialize primitive type"""
        self.name = name
        self.description = description
        self.offset = offset
        self.semanticType = semanticType
        self.encodingType = encodingType
        self.sinceVersion = sinceVersion
        self.deprecated = deprecated

        self.valid_value_name_map = {}
        self.valid_value_list = []


    def addValidValue(self, validValue: 'ValidValue') -> None:
        """add a valid value element to this enum"""
        if validValue.name in self.valid_value_name_map:
            raise DuplicateName(
                f'duplicate validValue name {repr(validValue.name)} already'
                f'defined in enum {repr(self.name)}'
            )

        self.valid_value_name_map[validValue.name] = validValue
        self.valid_value_list.append(validValue)


def createEnum(
        name: [str],
        encodingType: Optional[str]=None,
        description: Optional[str]=None,
        offset: Optional[int]=None,
        semanticType: Optional[str]=None,
        sinceVersion: Optional[int]=0,
        deprecated: Optional[int]=None,
) -> Enum:
    """create a new Type"""
    sbeEnum = Enum(
        name=name,
        encodingType=encodingType,
        description=description,
        offset=offset,
        semanticType=semanticType,
        sinceVersion=sinceVersion,
        deprecated=deprecated,
    )

    return sbeEnum


class ValidValue(BaseType):
    """An ValidValue for an Enum"""

    def __init__(
        self,
        name: [str],
        value: [str],
        description: Optional[str]=None,
        sinceVersion: Optional[int]=0,
        deprecated: Optional[int]=None,
    ) -> None:
        """initialize validValue type"""
        self.name = name
        self.description = description
        self.sinceVersion = sinceVersion
        self.deprecated = deprecated
        self.value = value


def createValidValue(
        name: [str],
        value: [str],
        description: Optional[str]=None,
        sinceVersion: Optional[int]=0,
        deprecated: Optional[int]=None,
) -> ValidValue:
    """create a new ValidValue"""
    valid_value = ValidValue(
        name=name,
        description=description,
        sinceVersion=sinceVersion,
        deprecated=deprecated,
        value=value,
    )

    return valid_value
