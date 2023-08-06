from enum import Enum

from serializers.xml import XmlSerializer
from serializers.json import JsonSerializer


class SerializerType(Enum):
    JSON = "json"
    XML = "xml"


class SerializersFactory:
    @staticmethod
    def create_serializer(st: SerializerType):

        if st == SerializerType.JSON:
            return JsonSerializer()

        elif st == SerializerType.XML:
            return XmlSerializer()

        else:
            raise Exception("Unknown type of serialization")
