from serializers.json_parser import Json
from serializers.xml_parser import Xml
from enum import Enum


class SerializerType(Enum):
    JSON = 0,
    XML = 1


class SerializerFactoryMethod:

    @staticmethod
    def make_serializer(serializer_type):
        if serializer_type == SerializerType.JSON:
            return Json()
        elif serializer_type == SerializerType.XML:
            return Xml()
        else:
            raise Exception("Parser does not exist!")
