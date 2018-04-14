"""types.py - schema for types type, composite, enum, etc"""
import weakref
from typing import Optional, Union
from .constants import PRESENCE, TYPE_PRIMITIVE_TYPE
from .exceptions import DuplicateName, DuplicateChoiceValue


class TypeCollection:
    """Holds map of types"""

    def __init__(self, *args, **kw):
        self.typesNameMap = {}
        self.typesList = []
        self.parentCollectionRef = None

    def addType(
        self, sbeType: Union["Type", "Composite", "Enum", "Ref", "Set"]
    ) -> None:
        """add a new type"""
        if sbeType.name in self.typesNameMap:
            raise DuplicateName(
                f"{sbeType.name}" " already registered in composite {self.name}"
            )

        if isinstance(sbeType, TypeCollection):
            sbeType.setParent(self)

        self.typesNameMap[sbeType.name] = sbeType
        self.typesList.append(sbeType)

    def setParent(self, parentCollection):
        """link this type collection with a parent"""
        self.parentCollectionRef = weakref.ref(parentCollection)

    def lookupName(self, name):
        """lookup name and return mapping or whatever"""
        if name in self.typesNameMap:
            return self.typesNameMap[name]

        if not self.parentCollectionRef:
            return None

        parentCollection = self.parentCollectionRef()
        if not parentCollection:
            return None

        return parentCollection.lookupName(name)


class AsDictType:

    def as_dict(self):
        """for debugging, return dict represenation"""
        d = self.__dict__.copy()
        d["__class__"] = self.__class__.__name__
        if "typesNameMap" in d:
            d["typesNameMap"] = {
                key: value.as_dict() for key, value in d["typesNameMap"].items()
            }

        if "fieldNameMap" in d:
            d["fieldNameMap"] = {
                key: value.as_dict() for key, value in d["fieldNameMap"].items()
            }
        for key, value in d.items():
            if isinstance(value, list) and len(value) and hasattr(value[0], "as_dict"):
                d[key] = [x.as_dict() for x in value]
            elif isinstance(value, dict):
                d[key] = {
                    ikey: ivalue.as_dict() if hasattr(ivalue, "as_dict") else ivalue
                    for ikey, ivalue in value.items()
                }

        return d


class BaseType(AsDictType):
    pass


class Type(BaseType):
    """A primitive Type"""

    def __init__(
        self,
        name: [str],
        primitiveType: [TYPE_PRIMITIVE_TYPE],
        presence: [PRESENCE],
        description: Optional[str] = None,
        nullValue: Optional[str] = None,
        minValue: Optional[str] = None,
        maxValue: Optional[str] = None,
        length: int = 1,
        offset: Optional[int] = None,
        semanticType: Optional[str] = None,
        sinceVersion: Optional[int] = 0,
        deprecated: Optional[int] = None,
        characterEncoding: Optional[str] = None,
        valueRef: Optional[str] = None,
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
    description: Optional[str] = None,
    nullValue: Optional[str] = None,
    minValue: Optional[str] = None,
    maxValue: Optional[str] = None,
    length: int = 1,
    offset: Optional[int] = None,
    semanticType: Optional[str] = None,
    sinceVersion: Optional[int] = 0,
    deprecated: Optional[int] = None,
    characterEncoding: Optional[str] = None,
    valueRef: Optional[str] = None,
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
        description: Optional[str] = None,
        offset: Optional[int] = None,
        semanticType: Optional[str] = None,
        sinceVersion: Optional[int] = 0,
        deprecated: Optional[int] = None,
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
    description: Optional[str] = None,
    offset: Optional[int] = None,
    semanticType: Optional[str] = None,
    sinceVersion: Optional[int] = 0,
    deprecated: Optional[int] = None,
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


class Ref(BaseType):
    """A Ref Type"""

    def __init__(
        self,
        name: [str],
        type: [str],
        offset: Optional[int] = None,
        sinceVersion: Optional[int] = 0,
        deprecated: Optional[int] = None,
    ) -> None:
        """initialize Ref type"""
        self.name = name
        self.offset = offset
        self.sinceVersion = sinceVersion
        self.deprecated = deprecated
        self.type = type


def createRef(
    name: [str],
    type: [str],
    offset: Optional[int] = None,
    sinceVersion: Optional[int] = 0,
    deprecated: Optional[int] = None,
) -> Ref:
    """create a new Type"""
    sbeRef = Ref(
        name=name,
        offset=offset,
        sinceVersion=sinceVersion,
        deprecated=deprecated,
        type=type,
    )

    return sbeRef


class Set(BaseType):
    """A Set Type"""

    def __init__(
        self,
        name: [str],
        description: Optional[str] = None,
        encodingType: Optional[str] = None,
        offset: Optional[int] = None,
        sinceVersion: Optional[int] = 0,
        deprecated: Optional[int] = None,
    ) -> None:
        """initialize Set type"""
        self.name = name
        self.offset = offset
        self.sinceVersion = sinceVersion
        self.deprecated = deprecated
        self.description = description
        self.encodingType = encodingType

        self.choice_name_map = {}
        self.choice_list = []
        self.choice_values = []

    def addChoice(self, choice: "Choice") -> None:
        """add a choice to this Set"""
        if choice.name in self.choice_name_map:
            raise DuplicateName(
                f"duplicate Choice name {repr(choice.name)} already"
                f"defined in set {repr(self.name)}"
            )

        self.choice_name_map[choice.name] = choice
        self.choice_list.append(choice)
        if choice.value in self.choice_values:
            raise DuplicateChoiceValue(
                f"set {self.name} choice name {choice.name}"
                f"value {repr(choice.value)} duplicates existing value"
            )

        self.choice_values.append(choice.value)


def createSet(
    name: [str],
    description: Optional[str] = None,
    encodingType: Optional[str] = None,
    offset: Optional[int] = None,
    sinceVersion: Optional[int] = 0,
    deprecated: Optional[int] = None,
) -> Set:
    """create a new Set"""
    sbeSet = Set(
        name=name,
        encodingType=encodingType,
        description=description,
        offset=offset,
        sinceVersion=sinceVersion,
        deprecated=deprecated,
    )

    return sbeSet


class Choice(BaseType):
    """A Choice for a Set"""

    def __init__(
        self,
        name: [str],
        value: [int],
        description: Optional[str] = None,
        sinceVersion: Optional[int] = 0,
        deprecated: Optional[int] = None,
    ) -> None:
        """initialize Choice type"""
        self.name = name
        self.description = description
        self.sinceVersion = sinceVersion
        self.deprecated = deprecated
        self.value = value
        self.bitmap = 1 << value


def createChoice(
    name: [str],
    value: [str],
    description: Optional[str] = None,
    sinceVersion: Optional[int] = 0,
    deprecated: Optional[int] = None,
) -> Choice:
    """create a new ValidValue"""
    choice = Choice(
        name=name,
        description=description,
        sinceVersion=sinceVersion,
        deprecated=deprecated,
        value=value,
    )

    return choice


class Enum(BaseType, TypeCollection):
    """An Enum"""

    def __init__(
        self,
        name: [str],
        encodingType: Optional[str] = None,
        description: Optional[str] = None,
        offset: Optional[int] = None,
        semanticType: Optional[str] = None,
        sinceVersion: Optional[int] = 0,
        deprecated: Optional[int] = None,
    ) -> None:
        """initialize primitive type"""
        super().__init__()
        self.name = name
        self.description = description
        self.offset = offset
        self.semanticType = semanticType
        self.encodingType = encodingType
        self.sinceVersion = sinceVersion
        self.deprecated = deprecated

        self.valid_value_name_map = {}
        self.valid_value_list = []

    def addValidValue(self, validValue: "ValidValue") -> None:
        """add a valid value element to this enum"""
        if validValue.name in self.valid_value_name_map:
            raise DuplicateName(
                f"duplicate validValue name {repr(validValue.name)} already"
                f"defined in enum {repr(self.name)}"
            )

        self.valid_value_name_map[validValue.name] = validValue
        self.valid_value_list.append(validValue)


def createEnum(
    name: [str],
    encodingType: Optional[str] = None,
    description: Optional[str] = None,
    offset: Optional[int] = None,
    semanticType: Optional[str] = None,
    sinceVersion: Optional[int] = 0,
    deprecated: Optional[int] = None,
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
        description: Optional[str] = None,
        sinceVersion: Optional[int] = 0,
        deprecated: Optional[int] = None,
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
    description: Optional[str] = None,
    sinceVersion: Optional[int] = 0,
    deprecated: Optional[int] = None,
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


class Message(AsDictType):
    """A message"""

    def __init__(
        self,
        name: [str],
        message_id: int,
        blockLength: Optional[int] = None,
        description: Optional[str] = None,
        semanticType: Optional[str] = None,
        sinceVersion: Optional[int] = 0,
        deprecated: Optional[int] = None,
    ) -> None:
        """create a new Message"""
        self.fieldNameMap = {}
        self.fieldList = []

        self.name = name
        self.message_id = message_id
        self.blockLength = blockLength
        self.description = description
        self.semanticType = semanticType
        self.sinceVersion = sinceVersion
        self.deprecated = deprecated

    def addField(self, field: "Field") -> None:
        """add a new type"""
        if field.name in self.fieldNameMap:
            raise DuplicateName(
                f"{field.name} already registered in message {self.name}"
            )

        self.fieldNameMap[field.name] = field
        self.fieldList.append(field)


def createMessage(
    name: [str],
    message_id: int,
    blockLength: Optional[int] = None,
    description: Optional[str] = None,
    semanticType: Optional[str] = None,
    sinceVersion: Optional[int] = 0,
    deprecated: Optional[int] = None,
) -> Message:
    """create a new message"""
    message = Message(
        name=name,
        message_id=message_id,
        blockLength=blockLength,
        description=description,
        semanticType=semanticType,
        sinceVersion=sinceVersion,
        deprecated=deprecated,
    )
    return message


class Field(AsDictType):
    """field specification"""

    def __init__(
        self,
        name: [str],
        field_id: [int],
        field_type: [str],
        description: [str] = None,
        offset: Optional[int] = None,
        presence: Optional[PRESENCE] = PRESENCE.REQUIRED,
        sinceVersion: Optional[int] = 0,
        deprecated: Optional[int] = None,
        valueRef: Optional[str] = None,
    ) -> None:
        """create a field"""
        self.name = name
        self.field_id = field_id
        self.field_type = field_type
        self.description = description
        self.offset = offset
        self.presence = presence
        self.sinceVersion = sinceVersion
        self.deprecated = deprecated
        self.valueRef = valueRef

    def validate(self, messageSchema: "MessageSchema", message: Message) -> None:
        """validate field attributes"""
        # check type
        resolved_type = messageSchema.lookupName(
            self.field_type
        )
        if not resolved_type:
            raise ValueError(
                f"field '{self.name}' type '{self.field_type}' could not be resolved, undefined type"
            )
        return


def createField(
    name: [str],
    field_id: [int],
    field_type: [str],
    description: [str] = None,
    offset: Optional[int] = None,
    presence: Optional[PRESENCE] = PRESENCE.REQUIRED,
    sinceVersion: Optional[int] = 0,
    deprecated: Optional[int] = None,
    valueRef: Optional[str] = None,
):
    """create a field"""
    field = Field(
        name=name,
        field_id=field_id,
        field_type=field_type,
        description=description,
        offset=offset,
        presence=presence,
        sinceVersion=sinceVersion,
        deprecated=deprecated,
        valueRef=valueRef,
    )

    return field
